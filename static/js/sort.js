function sortTableByColumn(table, columnIndex, type = "string") {
    const currentColumn = parseInt(table.dataset.sortColumn);
    const currentDirection = table.dataset.sortDir || "asc";

    let direction = "asc";
    if (currentColumn === columnIndex) direction = currentDirection === "asc" ? "desc" : "asc";

    const header = table.querySelectorAll("th")[columnIndex];
    const sortBy = header.id;
    updateURLParam(sortBy, direction);

    table.dataset.sortDir = direction;
    table.dataset.sortColumn = columnIndex;

    const rows = Array.from(table.tBodies[0].rows);

    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();

        let comparison = 0;
        if (type === "number") {
            comparison = parseFloat(aText) - parseFloat(bText);
        } else {
            comparison = aText.localeCompare(bText, undefined, { sensitivity: 'base' });
        }

        return direction === "asc" ? comparison : -comparison;
    });

    rows.forEach(row => table.tBodies[0].appendChild(row));

    table.querySelectorAll("th .arrow").forEach(arrow => arrow.textContent = "");
    const arrow = table.querySelectorAll("th")[columnIndex].querySelector(".arrow");
    if (arrow) arrow.textContent = direction === "asc" ? " ▲" : " ▼";
}

function updateURLParam(sortBy, sortOrder) {
    const url = new URL(window.location.href);
    url.searchParams.set("sort_by", sortBy);
    url.searchParams.set("sort_order", sortOrder);
    history.replaceState(null, "", url);
}

document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("book-table");
    const headers = table.querySelectorAll("thead th[data-col]");

    if (!table) return;

    function displaySortArrow(sortBy, sortOrder) {
        let columnIndex = -1;
        headers.forEach((th, idx) => {
            if (th.id === sortBy) columnIndex = idx+1; // +1 because first column is not sortable
        });

        if (columnIndex >= 0) {
            table.dataset.sortColumn = columnIndex;
            table.dataset.sortDir = sortOrder;

            table.querySelectorAll("th .arrow").forEach(arrow => arrow.textContent = "");
            const arrow = table.querySelectorAll("th")[columnIndex].querySelector(".arrow");
            if (arrow) arrow.textContent = sortOrder === "asc" ? " ▲" : " ▼";
        }
    }

    const urlParams = new URLSearchParams(window.location.search);
    const sortByParam = urlParams.get("sort_by");
    const sortOrderParam = urlParams.get("sort_order") || "asc";

    if (sortByParam) {
        displaySortArrow(sortByParam, sortOrderParam);
    } else {
        table.dataset.sortColumn = -1;
        table.dataset.sortDir = "asc";
    }

    headers.forEach(header => {
        const colIndex = parseInt(header.dataset.col);
        const type = header.dataset.type || "string";

        header.addEventListener("click", () => {
            sortTableByColumn(table, colIndex, type);
        });
    });
});
