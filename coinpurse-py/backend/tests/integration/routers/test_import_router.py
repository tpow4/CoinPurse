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

    def test_create_mapping_exact_duplicate(self, client, setup_data):
        """Should reject exact duplicate mappings (same institution + bank category + coinpurse category)"""
        # Create first mapping
        client.post(
            "/api/import/category-mappings",
            json={
                "institution_id": setup_data["institution"].institution_id,
                "bank_category_name": "Duplicate",
                "coinpurse_category_id": setup_data["category"].category_id,
            },
        )

        # Try exact duplicate (same triple)
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

    def test_create_mapping_same_bank_category_different_coinpurse(self, client, db_session, setup_data):
        """Should allow same bank category mapped to different coinpurse categories"""
        # Create a second category
        category2 = Category(name="Another Category")
        db_session.add(category2)
        db_session.commit()
        db_session.refresh(category2)

        # Create first mapping
        response1 = client.post(
            "/api/import/category-mappings",
            json={
                "institution_id": setup_data["institution"].institution_id,
                "bank_category_name": "Ambiguous",
                "coinpurse_category_id": setup_data["category"].category_id,
            },
        )
        assert response1.status_code == 201

        # Create second mapping with same bank category but different coinpurse category
        response2 = client.post(
            "/api/import/category-mappings",
            json={
                "institution_id": setup_data["institution"].institution_id,
                "bank_category_name": "Ambiguous",
                "coinpurse_category_id": category2.category_id,
                "priority": 2,
            },
        )
        assert response2.status_code == 201

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


class TestCategoryMappingGroupEndpoints:
    """Tests for batch category mapping group endpoints"""

    @pytest.fixture
    def setup_data(self, db_session):
        """Create test institution and categories"""
        institution = Institution(name="Group Bank")
        cats = [Category(name=n) for n in ["Food", "Travel", "Bills"]]
        db_session.add(institution)
        db_session.add_all(cats)
        db_session.commit()
        db_session.refresh(institution)
        for c in cats:
            db_session.refresh(c)
        return {"institution": institution, "categories": cats}

    def test_save_group_create_new(self, client, setup_data):
        """Should create a new mapping group in one call"""
        inst = setup_data["institution"]
        cats = setup_data["categories"]

        response = client.put(
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Dining",
                "coinpurse_category_ids": [cats[0].category_id, cats[1].category_id],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(m["bank_category_name"] == "Dining" for m in data)
        returned_cat_ids = {m["coinpurse_category_id"] for m in data}
        assert returned_cat_ids == {cats[0].category_id, cats[1].category_id}

    def test_save_group_add_category(self, client, db_session, setup_data):
        """Should add a category to an existing group"""
        inst = setup_data["institution"]
        cats = setup_data["categories"]

        # Create initial group with one category
        mapping = CategoryMapping(
            institution_id=inst.institution_id,
            bank_category_name="Groceries",
            coinpurse_category_id=cats[0].category_id,
        )
        db_session.add(mapping)
        db_session.commit()

        # Save group with two categories
        response = client.put(
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Groceries",
                "coinpurse_category_ids": [cats[0].category_id, cats[1].category_id],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_save_group_remove_category(self, client, db_session, setup_data):
        """Should remove a category from an existing group"""
        inst = setup_data["institution"]
        cats = setup_data["categories"]

        # Create initial group with two categories
        for c in cats[:2]:
            db_session.add(
                CategoryMapping(
                    institution_id=inst.institution_id,
                    bank_category_name="Mixed",
                    coinpurse_category_id=c.category_id,
                )
            )
        db_session.commit()

        # Save group keeping only one
        response = client.put(
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Mixed",
                "coinpurse_category_ids": [cats[0].category_id],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["coinpurse_category_id"] == cats[0].category_id

    def test_save_group_rename(self, client, db_session, setup_data):
        """Should rename a mapping group"""
        inst = setup_data["institution"]
        cats = setup_data["categories"]

        mapping = CategoryMapping(
            institution_id=inst.institution_id,
            bank_category_name="Old Name",
            coinpurse_category_id=cats[0].category_id,
        )
        db_session.add(mapping)
        db_session.commit()

        response = client.put(
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "New Name",
                "coinpurse_category_ids": [cats[0].category_id],
                "old_bank_category_name": "Old Name",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["bank_category_name"] == "New Name"

        # Verify old name no longer exists
        list_response = client.get(
            f"/api/import/category-mappings?institution_id={inst.institution_id}"
        )
        names = {m["bank_category_name"] for m in list_response.json()}
        assert "Old Name" not in names
        assert "New Name" in names

    def test_save_group_rename_conflict(self, client, db_session, setup_data):
        """Should reject rename if new name conflicts with existing group"""
        inst = setup_data["institution"]
        cats = setup_data["categories"]

        # Create two groups
        db_session.add(
            CategoryMapping(
                institution_id=inst.institution_id,
                bank_category_name="Group A",
                coinpurse_category_id=cats[0].category_id,
            )
        )
        db_session.add(
            CategoryMapping(
                institution_id=inst.institution_id,
                bank_category_name="Group B",
                coinpurse_category_id=cats[1].category_id,
            )
        )
        db_session.commit()

        # Try to rename Group A to Group B
        response = client.put(
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Group B",
                "coinpurse_category_ids": [cats[0].category_id],
                "old_bank_category_name": "Group A",
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_save_group_duplicate_category_ids(self, client, setup_data):
        """Should reject duplicate category IDs in request"""
        inst = setup_data["institution"]
        cats = setup_data["categories"]

        response = client.put(
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Dupes",
                "coinpurse_category_ids": [cats[0].category_id, cats[0].category_id],
            },
        )

        assert response.status_code == 400
        assert "Duplicate" in response.json()["detail"]

    def test_save_group_empty_categories(self, client, setup_data):
        """Should reject empty category list"""
        inst = setup_data["institution"]

        response = client.put(
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Empty",
                "coinpurse_category_ids": [],
            },
        )

        assert response.status_code == 422  # Pydantic validation (min_length=1)

    def test_save_group_rename_and_change_categories(self, client, db_session, setup_data):
        """Should rename and modify categories in a single call"""
        inst = setup_data["institution"]
        cats = setup_data["categories"]

        # Create group with cats[0] and cats[1]
        for c in cats[:2]:
            db_session.add(
                CategoryMapping(
                    institution_id=inst.institution_id,
                    bank_category_name="Original",
                    coinpurse_category_id=c.category_id,
                )
            )
        db_session.commit()

        # Rename and swap cats[1] for cats[2]
        response = client.put(
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Renamed",
                "coinpurse_category_ids": [cats[0].category_id, cats[2].category_id],
                "old_bank_category_name": "Original",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(m["bank_category_name"] == "Renamed" for m in data)
        returned_cat_ids = {m["coinpurse_category_id"] for m in data}
        assert returned_cat_ids == {cats[0].category_id, cats[2].category_id}

    def test_delete_group(self, client, db_session, setup_data):
        """Should delete all mappings in a group"""
        inst = setup_data["institution"]
        cats = setup_data["categories"]

        for c in cats[:2]:
            db_session.add(
                CategoryMapping(
                    institution_id=inst.institution_id,
                    bank_category_name="Delete Me",
                    coinpurse_category_id=c.category_id,
                )
            )
        db_session.commit()

        response = client.request(
            "DELETE",
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Delete Me",
            },
        )

        assert response.status_code == 204

        # Verify deleted
        list_response = client.get(
            f"/api/import/category-mappings?institution_id={inst.institution_id}"
        )
        assert len(list_response.json()) == 0

    def test_delete_group_not_found(self, client, setup_data):
        """Should return 404 when deleting a non-existent group"""
        inst = setup_data["institution"]

        response = client.request(
            "DELETE",
            "/api/import/category-mappings/group",
            json={
                "institution_id": inst.institution_id,
                "bank_category_name": "Nonexistent",
            },
        )

        assert response.status_code == 404


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
        data = {"account_id": setup_import_data["account"].account_id}

        response = client.post("/api/import/upload", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "import_batch_id" in result
        assert result["summary"]["total_rows"] == 2
        assert result["summary"]["valid_rows"] == 2
        assert len(result["transactions"]) == 2

    def test_upload_account_without_template(self, client, db_session, setup_import_data):
        """Should return error when account has no template configured"""
        # Create account without template
        account_no_template = Account(
            institution_id=setup_import_data["institution"].institution_id,
            account_name="No Template Account",
            account_type=AccountType.CREDIT_CARD,
            tax_treatment=TaxTreatmentType.NOT_APPLICABLE,
            last_4_digits="0000",
            tracks_transactions=True,
            template_id=None,
        )
        db_session.add(account_no_template)
        db_session.commit()
        db_session.refresh(account_no_template)

        csv_content = "Transaction Date,Description,Amount\n1/15/2026,Test,100"

        files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        data = {"account_id": account_no_template.account_id}

        response = client.post("/api/import/upload", files=files, data=data)

        assert response.status_code == 422
        assert "no import template configured" in response.json()["detail"]


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
        data = {"account_id": account.account_id}

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

    def test_confirm_with_category_override(self, client, db_session, setup_with_preview):
        """Should use overridden category when category_overrides provided"""
        # Create a category to override with
        override_category = Category(name="Override Category")
        db_session.add(override_category)
        db_session.commit()
        db_session.refresh(override_category)

        # Confirm with override for row 2
        response = client.post(
            "/api/import/confirm",
            json={
                "import_batch_id": setup_with_preview["import_batch_id"],
                "selected_rows": [2, 3],
                "category_overrides": {
                    "2": override_category.category_id,
                },
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert result["imported_count"] == 2
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
        data = {"account_id": account.account_id}

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
        assert all(
            b["account_id"] == setup_with_batches["account"].account_id for b in data
        )

    def test_get_batch_detail(self, client, setup_with_batches):
        """Should get batch details"""
        response = client.get(
            f"/api/import/batches/{setup_with_batches['import_batch_id']}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["import_batch_id"] == setup_with_batches["import_batch_id"]
        assert data["status"] == "completed"
        assert "account_name" in data
