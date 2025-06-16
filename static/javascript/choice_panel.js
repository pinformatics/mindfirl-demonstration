/*
    Author: Qinbo Li
    Date: 10/17/2017
    Requirement: jquery-3.2.1
    This file defines the behavior of the choice-panel
*/

$(document).ready(function(){
    $(document).on("click", "li.input_radio", function(e) {
        console.log('clickityclick')
        e.preventDefault();
        e.stopPropagation();
        $(this).parent().find("li.input_radio").removeClass("ion-android-radio-button-on");
        $(this).parent().find("li.input_radio").addClass("ion-android-radio-button-off");
        $(this).removeClass("ion-android-radio-button-off");
        $(this).addClass("ion-android-radio-button-on");
        var $selected_id = $(this).attr("id");
        console.log($selected_id)
        var $diff = $(this).parent().parent().find("li.diff");
        var $same = $(this).parent().parent().find("li.same");
        if($selected_id.indexOf("a1") > 0 || $selected_id.indexOf("a2") > 0 || $selected_id.indexOf("a3") > 0) {
            $diff.css("border-color", "#30819c");
            $same.css("border-color", "transparent");
        }
        else {
            $diff.css("border-color", "transparent");
            $same.css("border-color", "#30819c");
        }

        fetch('/update_selection', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'id': $selected_id})

        })
    });
})


$(document).ready(function() {
    var $options = $(".submit-button");
    console.log("at least it ran")

    $options.click(function(e) {
        e.preventDefault()
        console.log("submit selections")
        fetch('/submit_selections', {
            method: 'POST',
            credentials: 'same-origin'
        })
        .then(response => {
            alert("Thank you for participating! Your submissions have been recorded. " + 
                "If you would like to change your submissions, you may do so and then resubmit. After a short time, we " + 
                "will display the group's selections.")
        })
        .catch(error => {
            // handle error here
        });
    });
})