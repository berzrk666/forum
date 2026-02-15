export function renderBreadcrumb(items) {
  const crumbs = items
    .map((item, i) => {
      if (i === items.length - 1) {
        return `<span>${item.label}</span>`;
      }
      return `<a href="${item.href}">${item.label}</a>`;
    })
    .join('<span class="breadcrumb-bar__separator">&rsaquo;</span>');

  return `
    <div class="breadcrumb-bar">
      ${crumbs}
    </div>
  `;
}
