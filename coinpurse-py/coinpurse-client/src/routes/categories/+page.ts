import { redirect } from '@sveltejs/kit';
import { localizeHref } from '$lib/paraglide/runtime';

export function load() {
    redirect(301, localizeHref('/settings/categories'));
}
