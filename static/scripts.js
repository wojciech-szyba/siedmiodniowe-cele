function set_achieved(divId) {
    document.location.href = '/goal_achieved/' + divId;
}

function moveUpNonEmptyCells() {
    const table = document.querySelectorAll('tbody');

    for (let i = 0; i < table.length; i++) {
        const rows = Array.from(table[i].querySelectorAll('tr'));
        // For each column
        for (let i = 0; i < rows.length; i++) {
        rows[0].querySelectorAll('td, th').forEach((header, colIndex) => {
            // Skip if no header
            if (!header) return;

            const columnCells = rows.map(row => row.children[colIndex]).filter(Boolean);

            // Shift non-empty cells up to fill empty slots
            for (let i = 0; i < columnCells.length - 1; i++) {
                const current = columnCells[i];
                const next = columnCells[i + 1];

                if (!current.textContent.trim() && next.textContent.trim()) {
                    // Move content up
                    current.innerHTML = next.innerHTML;
                    next.innerHTML = '';
                }
            }
        })
        }
    }
}

function openGoalModal(op, startWeek, dayId, goalId) {
    if (op == "add_goal") {
        fetch(`/add_goal/${startWeek}/${dayId}`, {
                method: 'GET'
            })
            .then(response => response.text())
            .then(html => {
                document.getElementById('modal-body').innerHTML = html;
                document.getElementById('goal-modal').style.display = 'block';
            });
    }
    else if (op == "update_goal")  {
        fetch(`/update_goal/${goalId}`, {  // ← Fixed
                method: 'GET'
            })
            .then(response => response.text())
            .then(html => {
                document.getElementById('modal-body').innerHTML = html;
                document.getElementById('goal-modal').style.display = 'block';
            });
    }
}

function closeModal() {
    document.getElementById('goal-modal').style.display = 'none';
}
