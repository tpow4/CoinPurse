"""
Integration tests for Import Router
"""

import io

import pytest

from models import (
    Account,
    AccountType,
    Category,
    CategoryMapping,
    FileFormat,
    ImportTemplate,
    Institution,
    TaxTreatmentType,
)


class TestImportTemplateEndpoints:
    """Tests for import template CRUD endpoints"""

    def test_create_template(self, client):
        """Should create an import template"""
        response = client.post(
            "/api/import/templates",
            json={
                "template_name": "Test Template",
                "file_format": "csv",
                "column_mappings": {
                    "transaction_date": "Date",
                    "posted_date": "Post Date",
                    "description": "Description",
                    "amount": "Amount",
                },
                "amount_config": {
                    "sign_convention": "bank_standard",
                    "decimal_places": 2,
                },
                "date_format": "%m/%d/%Y",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["template_name"] == "Test Template"
        assert data["file_format"] == "csv"

    def test_create_template_duplicate_name(self, client):
        """Should reject duplicate template names"""
        # Create first template
        client.post(
            "/api/import/templates",
            json={
                "template_name": "Duplicate Name",
                "file_format": "csv",
                "column_mappings": {
                    "transaction_date": "Transaction Date",
                    "posted_date": "Post Date",
                    "amount": "Amount",
                },
                "amount_config": {"sign_convention": "bank_standard"},
            },
        )

        # Try to create duplicate
        response = client.post(
            "/api/import/templates",
            json={
                "template_name": "Duplicate Name",
                "file_format": "csv",
                "column_mappings": {
                    "transaction_date": "Transaction Date",
                    "posted_date": "Post Date",
                    "amount": "Amount",
                },
                "amount_config": {"sign_convention": "bank_standard"},
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_list_templates(self, client, db_session):
        """Should list all templates"""
        # Create templates
        for i in range(3):
            template = ImportTemplate(
                template_name=f"Template {i}",
                file_format=FileFormat.CSV,
                column_mappings={
                    "transaction_date": "Transaction Date",
                    "posted_date": "Post Date",
                    "amount": "Amount",
                },
                amount_config={"sign_convention": "bank_standard"},
            )
            db_session.add(template)
        db_session.commit()

        response = client.get("/api/import/templates")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_template(self, client, db_session):
        """Should get a specific template"""
        template = ImportTemplate(
            template_name="Get Me",
            file_format=FileFormat.CSV,
            column_mappings={
                "transaction_date": "Transaction Date",
                "posted_date": "Post Date",
                "amount": "Amount",
            },
            amount_config={"sign_convention": "bank_standard"},
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        response = client.get(f"/api/import/templates/{template.template_id}")

        assert response.status_code == 200
        assert response.json()["template_name"] == "Get Me"

    def test_get_template_not_found(self, client):
        """Should return 404 for unknown template"""
        response = client.get("/api/import/templates/99999")
        assert response.status_code == 404

    def test_update_template(self, client, db_session):
        """Should update a template"""
        template = ImportTemplate(
            template_name="Original Name",
            file_format=FileFormat.CSV,
            column_mappings={
                "transaction_date": "Transaction Date",
                "posted_date": "Post Date",
                "amount": "Amount",
            },
            amount_config={"sign_convention": "bank_standard"},
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        response = client.patch(
            f"/api/import/templates/{template.template_id}",
            json={"template_name": "Updated Name"},
        )

        assert response.status_code == 200
        assert response.json()["template_name"] == "Updated Name"

    def test_delete_template_soft(self, client, db_session):
        """Should soft delete a template"""
        template = ImportTemplate(
            template_name="Delete Me",
            file_format=FileFormat.CSV,
            column_mappings={
                "transaction_date": "Transaction Date",
                "posted_date": "Post Date",
                "amount": "Amount",
            },
            amount_config={"sign_convention": "bank_standard"},
        )
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)

        response = client.delete(f"/api/import/templates/{template.template_id}")

        assert response.status_code == 204

        # Verify soft deleted
        db_session.refresh(template)
        assert template.is_active is False


class TestCategoryMappingEndpoints:
    """Tests for category mapping CRUD endpoints"""

    @pytest.fixture
    def setup_data(self, db_session):
        """Create test institution and category"""
        institution = Institution(name="Mapping Bank")
        category = Category(name="Test Category")
        db_session.add_all([institution, category])
        db_session.commit()
        db_session.refresh(institution)
        db_session.refresh(category)
        return {"institution": institution, "category": category}

    def test_create_mapping(self, client, setup_data):
        """Should create a category mapping"""
        response = client.post(
            "/api/import/category-mappings",
            json={
                "institution_id": setup_data["institution"].institution_id,
                "bank_category_name": "Bank Category",
                "coinpurse_category_id": setup_data["category"].category_id,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["bank_category_name"] == "Bank Category"

    def test_create_mapping_duplicate(self, client, setup_data):
        """Should reject duplicate mappings"""
        # Create first mapping
        client.post(
            "/api/import/category-mappings",
            json={
                "institution_id": setup_data["institution"].institution_id,
                "bank_category_name": "Duplicate",
                "coinpurse_category_id": setup_data["category"].category_id,
            },
        )

        # Try duplicate
        response = client.post(
            "/api/import/category-mappings",
            json={
                "institution_id": setup_data["institution"].institution_id,
                "bank_category_name": "Duplicate",
                "coinpurse_category_id": setup_data["category"].category_id,
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_list_mappings_by_institution(self, client, db_session, setup_data):
        """Should filter mappings by institution"""
        # Create mappings
        mapping = CategoryMapping(
            institution_id=setup_data["institution"].institution_id,
            bank_category_name="Test",
            coinpurse_category_id=setup_data["category"].category_id,
        )
        db_session.add(mapping)
        db_session.commit()

        response = client.get(
            f"/api/import/category-mappings?institution_id={setup_data['institution'].institution_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestImportUploadEndpoint:
    """Tests for the upload and preview endpoint"""

    @pytest.fixture
    def setup_import_data(self, db_session):
        """Set up all required data for import tests"""
        # Create institution
        institution = Institution(name="Import Bank")
        db_session.add(institution)
        db_session.commit()

        # Create category
        uncategorized = Category(name="Uncategorized")
        db_session.add(uncategorized)
        db_session.commit()

        # Create template (Chase-like)
        template = ImportTemplate(
            template_name="Test Import Template",
            file_format=FileFormat.CSV,
            column_mappings={
                "transaction_date": "Transaction Date",
                "posted_date": "Post Date",
                "description": "Description",
                "amount": "Amount",
                "category": "Category",
            },
            amount_config={
                "sign_convention": "bank_standard",
                "decimal_places": 2,
            },
            date_format="%m/%d/%Y",
        )
        db_session.add(template)
        db_session.commit()

        # Create account with template
        account = Account(
            institution_id=institution.institution_id,
            template_id=template.template_id,
            account_name="Import Account",
            account_type=AccountType.CREDIT_CARD,
            tax_treatment=TaxTreatmentType.NOT_APPLICABLE,
            last_4_digits="9999",
            tracks_transactions=True,
        )
        db_session.add(account)
        db_session.commit()

        db_session.refresh(institution)
        db_session.refresh(uncategorized)
        db_session.refresh(account)
        db_session.refresh(template)

        return {
            "institution": institution,
            "category": uncategorized,
            "account": account,
            "template": template,
        }

    def test_upload_csv_preview(self, client, setup_import_data):
        """Should upload CSV and return preview"""
        csv_content = """Transaction Date,Post Date,Description,Category,Amount
1/15/2026,1/15/2026,Test Payment,,100.00
1/16/2026,1/16/2026,Test Purchase,Shopping,-50.00"""

        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        data = {
            "account_id": setup_import_data["account"].account_id,
            "template_id": setup_import_data["template"].template_id,
        }

        response = client.post("/api/import/upload", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "import_batch_id" in result
        assert result["summary"]["total_rows"] == 2
        assert result["summary"]["valid_rows"] == 2
        assert len(result["transactions"]) == 2

    def test_upload_invalid_template(self, client, setup_import_data):
        """Should return error for invalid template"""
        csv_content = "Transaction Date,Description,Amount\n1/15/2026,Test,100"

        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        data = {
            "account_id": setup_import_data["account"].account_id,
            "template_id": 99999,  # Invalid
        }

        response = client.post("/api/import/upload", files=files, data=data)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]


class TestImportConfirmEndpoint:
    """Tests for the confirm import endpoint"""

    @pytest.fixture
    def setup_with_preview(self, client, db_session):
        """Set up data and create a preview batch"""
        # Create institution
        institution = Institution(name="Confirm Bank")
        db_session.add(institution)
        db_session.commit()

        # Create category
        uncategorized = Category(name="Uncategorized")
        db_session.add(uncategorized)
        db_session.commit()

        # Create template
        template = ImportTemplate(
            template_name="Confirm Template",
            file_format=FileFormat.CSV,
            column_mappings={
                "transaction_date": "Date",
                "posted_date": "Posted Date",
                "description": "Desc",
                "amount": "Amt",
            },
            amount_config={"sign_convention": "bank_standard", "decimal_places": 2},
            date_format="%m/%d/%Y",
        )
        db_session.add(template)
        db_session.commit()

        # Create account with template
        account = Account(
            institution_id=institution.institution_id,
            template_id=template.template_id,
            account_name="Confirm Account",
            account_type=AccountType.CREDIT_CARD,
            tax_treatment=TaxTreatmentType.NOT_APPLICABLE,
            last_4_digits="8888",
            tracks_transactions=True,
        )
        db_session.add(account)
        db_session.commit()

        db_session.refresh(account)
        db_session.refresh(template)

        # Upload to create preview
        csv_content = """Date,Posted Date,Desc,Amt
1/15/2026,1/15/2026,Payment,100.00
1/16/2026,1/16/2026,Purchase,-50.00
1/17/2026,1/17/2026,Another,-25.00"""

        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        data = {"account_id": account.account_id, "template_id": template.template_id}

        preview_response = client.post("/api/import/upload", files=files, data=data)
        preview = preview_response.json()

        return {
            "account": account,
            "template": template,
            "import_batch_id": preview["import_batch_id"],
            "transactions": preview["transactions"],
        }

    def test_confirm_import(self, client, setup_with_preview):
        """Should confirm and import selected rows"""
        response = client.post(
            "/api/import/confirm",
            json={
                "import_batch_id": setup_with_preview["import_batch_id"],
                "selected_rows": [2, 3],  # Import first two data rows
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert result["imported_count"] == 2
        assert result["skipped_count"] == 1  # Third row not selected
        assert result["status"] == "completed"

    def test_confirm_invalid_batch(self, client):
        """Should return error for invalid batch"""
        response = client.post(
            "/api/import/confirm",
            json={"import_batch_id": 99999, "selected_rows": [1]},
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]


class TestImportBatchEndpoints:
    """Tests for batch history endpoints"""

    @pytest.fixture
    def setup_with_batches(self, client, db_session):
        """Set up data with completed batches"""
        # Create institution
        institution = Institution(name="Batch Bank")
        db_session.add(institution)
        db_session.commit()

        # Create category
        uncategorized = Category(name="Uncategorized")
        db_session.add(uncategorized)
        db_session.commit()

        # Create template
        template = ImportTemplate(
            template_name="Batch Template",
            file_format=FileFormat.CSV,
            column_mappings={
                "transaction_date": "Date",
                "posted_date": "Posted Date",
                "description": "Desc",
                "amount": "Amt",
            },
            amount_config={"sign_convention": "bank_standard", "decimal_places": 2},
            date_format="%m/%d/%Y",
        )
        db_session.add(template)
        db_session.commit()

        # Create account with template
        account = Account(
            institution_id=institution.institution_id,
            template_id=template.template_id,
            account_name="Batch Account",
            account_type=AccountType.CREDIT_CARD,
            tax_treatment=TaxTreatmentType.NOT_APPLICABLE,
            last_4_digits="7777",
            tracks_transactions=True,
        )
        db_session.add(account)
        db_session.commit()

        db_session.refresh(account)
        db_session.refresh(template)

        # Create and confirm a batch
        csv_content = "Date,Posted Date,Desc,Amt\n1/15/2026,1/15/2026,Test,100.00"
        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        data = {"account_id": account.account_id, "template_id": template.template_id}

        preview = client.post("/api/import/upload", files=files, data=data).json()
        client.post(
            "/api/import/confirm",
            json={"import_batch_id": preview["import_batch_id"], "selected_rows": [2]},
        )

        return {"account": account, "import_batch_id": preview["import_batch_id"]}

    def test_list_batches(self, client, setup_with_batches):
        """Should list import batches"""
        response = client.get("/api/import/batches")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_list_batches_by_account(self, client, setup_with_batches):
        """Should filter batches by account"""
        response = client.get(
            f"/api/import/batches?account_id={setup_with_batches['account'].account_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert all(b["account_id"] == setup_with_batches["account"].account_id for b in data)

    def test_get_batch_detail(self, client, setup_with_batches):
        """Should get batch details"""
        response = client.get(f"/api/import/batches/{setup_with_batches['import_batch_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["import_batch_id"] == setup_with_batches["import_batch_id"]
        assert data["status"] == "completed"
        assert "account_name" in data
