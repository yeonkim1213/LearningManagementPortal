import { $ } from "/static/jquery/src/jquery.js";

export function say_hi(elt) {
    console.log("Say hi to", elt);
}

say_hi($("h1"));

export function make_table_sortable($table) {
    const $headers = $table.find('thead th.sortable');

    $table.find('tbody tr').not('.no-sort').each(function(index) {
        $(this).attr('data-original-index', index);
    });

    $headers.on('click', function() {
        let $this = $(this);
        let sortState = $this.data('sort-state') || 'original'; 

        $headers.removeClass('sort-asc sort-desc').data('sort-state', 'original');

        if (sortState === 'original') {
            $this.addClass('sort-asc').data('sort-state', 'asc');
        } else if (sortState === 'asc') {
            $this.addClass('sort-desc').data('sort-state', 'desc');
        } else {
            $this.data('sort-state', 'original');
        }

        let columnIndex = $this.index();
        let rows = $table.find('tbody tr').not('.no-sort').toArray();

        if (sortState !== 'original') {
            rows.sort(function(tr1, tr2) {
                let val1 = $(tr1).find(`td:eq(${columnIndex})`).text();
                let val2 = $(tr2).find(`td:eq(${columnIndex})`).text();
                if ($this.hasClass('date-column')) {
                    val1 = new Date(val1).getTime();
                    val2 = new Date(val2).getTime();
                }

                if (isNaN(val1) || isNaN(val2)) {
                    return sortState === 'asc' ? val1.localeCompare(val2) : val2.localeCompare(val1);
                } else {
                    val1 = parseFloat(val1);
                    val2 = parseFloat(val2);
                    return sortState === 'asc' ? val1 - val2 : val2 - val1;
                }
            });
        } else {

            rows.sort(function(tr1, tr2) {
                return $(tr1).data('original-index') - $(tr2).data('original-index');
            });
        }


        $(rows).appendTo($table.find('tbody'));

        const $noSortRow = $table.find('tbody tr.no-sort').detach();
        $noSortRow.appendTo($table.find('tbody'));
    });
}

function computeCurrentGrade($table) {
    let cumulativeWeight = 0;
    let cumulativePoints = 0;

    $table.find('tbody tr').each(function() {
        const $currentRow = $(this);
        const assignmentWeight = parseFloat($currentRow.data('weight'));
        let assignmentScore;

        if ($table.hasClass('hypothesized')) {
            const hypoInputVal = $currentRow.find('input').val();
            assignmentScore = hypoInputVal ? parseFloat(hypoInputVal) : null;
        } else {
            const recordedGrade = $currentRow.find('td[data-value]').text();
            assignmentScore = (!isNaN(recordedGrade) && recordedGrade !== 'Not Due' && recordedGrade !== 'Ungraded') ? parseFloat(recordedGrade) : null;
        }

        if (assignmentScore !== null) {
            cumulativeWeight += assignmentWeight;
            cumulativePoints += assignmentScore * assignmentWeight;
        }
    });

    const computedFinalGrade = cumulativeWeight > 0 ? (cumulativePoints / cumulativeWeight) : 0;
    $table.find('.finalGrade').text(computedFinalGrade.toFixed(2) + '%');
}

export function make_grade_hypothesized($table) {
    const toggleButton = $('<button>Hypothesize</button>');
    $table.before(toggleButton);

    toggleButton.on('click', function() {
        const isHypothesizing = $table.hasClass('hypothesized');
      
        $table.toggleClass('hypothesized', !isHypothesizing);
        toggleButton.text(isHypothesizing ? 'Hypothesize' : 'Actual grades');

        $table.find('td').each(function() {
            let cell = $(this);


            if (isHypothesizing && cell.data('original-text')) {
            
                cell.text(cell.data('original-text'));
            }
            
            else {
                const gradeText = cell.text().trim();
                if (gradeText === 'Not Due' || gradeText === 'Ungraded') {
                   
                    cell.data('original-text', gradeText)
                        .html('<input type="number" min="0" max="100" step="0.01">');
                }
            }
        });

        recalculateGrade($table);
    });

    
    $table.on('input', 'input', function() {
        recalculateGrade($table);
    });


    function recalculateGrade(table) {
        computeCurrentGrade(table);
    }
}

export function make_form_async(form) {
    form.on('submit', function(submitEvent) {
        submitEvent.preventDefault(); 

        form.find('input[type="file"], button').prop('disabled', true);

        let submittedData = new FormData(this);

        $.ajax({
            url: form.attr('action'), 
            method: 'POST', 
            data: submittedData,
            processData: false, 
            contentType: false,
            mimeType: form.attr('enctype'),

            success: () => {
                form.empty().append('<p>Sucessful</p>');
            },

            error: () => {
                console.error('Error');
                form.find('input[type="file"], button').prop('disabled', false);
                form.append('<p class="error">Error</p>');
            }
        });
    });
}
