function addColumnPager(tableSelector, colsPerPage = 3) {
    const table = document.querySelector(tableSelector);
    const rows = table.querySelectorAll("tr");

    // Get the total number of columns
    const colCount = rows[0].children.length;
    const numPages = Math.ceil(colCount / colsPerPage);

    // Create pager
    const pagerDiv = document.createElement("div");
    pagerDiv.className = "column-nav";

    for (let i = 0; i < numPages; i++) {
        const a = document.createElement("a");
        a.href = "#";
        a.textContent = i + 1;
        a.dataset.page = i;
        a.addEventListener("click", e => {
            e.preventDefault();
            changeToColumnPage(table, i, colsPerPage);
        });
        pagerDiv.appendChild(a);
    }

    // Insert pager after table
    table.parentNode.insertBefore(pagerDiv, table.nextSibling);

    // Show the first page
    changeToColumnPage(table, 0, colsPerPage);
}

function changeToColumnPage(table, pageIndex, colsPerPage) {
    const startCol = pageIndex * colsPerPage;
    const endCol = startCol + colsPerPage;

    // Go through each row
    const rows = table.querySelectorAll("tr");
    for (const row of rows) {
        const cells = row.children;
        for (let i = 0; i < cells.length; i++) {
            cells[i].style.display = (i >= startCol && i < endCol) ? "" : "none";
        }
    }

    // Highlight current page
    const nav = table.nextSibling;
    const links = nav.querySelectorAll("a");
    links.forEach((link, i) => {
        link.classList.toggle("active", i === pageIndex);
    });
}





// console.log("start js")
// addPagerToTables('#mobile-table', 4);

// function addPagerToTables(tables, rowsPerPage = 10) {
//     console.log("pager")

//     tables = 
//         typeof tables == "string"
//       ? document.querySelectorAll(tables)
//       : tables;

//     for (let table of tables) 
//         addPagerToTable(table, rowsPerPage);

// }

// function addPagerToTable(table, rowsPerPage = 10) {

//     let tBodyRows = getBodyRows(table);
//     let numPages = Math.ceil(tBodyRows.length/rowsPerPage);

//     let colCount = 
//       [].slice.call(
//           table.querySelector('tr').cells
//       )
//       .reduce((a,b) => a + parseInt(b.colSpan), 0);

//     table
//     .createTFoot()
//     .insertRow()
//     .innerHTML = `<td colspan=${colCount}><div class="nav"></div></td>`;

//     if(numPages == 1)
//         return;

//     for(i = 0;i < numPages;i++) {

//         let pageNum = i + 1;

//         table.querySelector('.nav')
//         .insertAdjacentHTML(
//             'beforeend',
//             `<a href="#" rel="${i}">${pageNum}</a> `        
//         );

//     }

//     changeToPage(table, 1, rowsPerPage);

//     for (let navA of table.querySelectorAll('.nav a'))
//         navA.addEventListener(
//             'click', 
//             e => changeToPage(
//                 table, 
//                 parseInt(e.target.innerHTML), 
//                 rowsPerPage
//             )
//         );

// }

// function changeToPage(table, page, rowsPerPage) {

//     let startItem = (page - 1) * rowsPerPage;
//     let endItem = startItem + rowsPerPage;
//     let navAs = table.querySelectorAll('.nav a');
//     let tBodyRows = getBodyRows(table);

//     for (let nix = 0; nix < navAs.length; nix++) {

//         if (nix == page - 1)
//             navAs[nix].classList.add('active');
//         else 
//             navAs[nix].classList.remove('active');

//         for (let trix = 0; trix < tBodyRows.length; trix++) 
//             tBodyRows[trix].style.display = 
//                 (trix >= startItem && trix < endItem)
//                 ? 'table-row'
//                 : 'none';  

//     }

// }

// // tbody might still capture header rows if 
// // if a thead was not created explicitly.
// // This filters those rows out.
// function getBodyRows(table) {
//     let initial = table.querySelectorAll('tbody tr');
//   return Array.from(initial)
//     .filter(row => row.querySelectorAll('td').length > 0);
// }