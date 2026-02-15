export function renderPagination(currentPage, totalPages) {
  if (totalPages <= 1) return "";

  let items = "";

  items += currentPage > 1
    ? `<span class="pagination__item" data-page="${currentPage - 1}">&laquo; Prev</span>`
    : `<span class="pagination__item pagination__item--disabled">&laquo; Prev</span>`;

  for (let i = 1; i <= totalPages; i++) {
    const active = i === currentPage ? " pagination__item--active" : "";
    items += `<span class="pagination__item${active}" data-page="${i}">${i}</span>`;
  }

  items += currentPage < totalPages
    ? `<span class="pagination__item" data-page="${currentPage + 1}">Next &raquo;</span>`
    : `<span class="pagination__item pagination__item--disabled">Next &raquo;</span>`;

  return `<div class="pagination">${items}</div>`;
}
