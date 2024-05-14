$(document).ready(function() {
    $("#specialty").change(function(){
        $('#subSpecialty').empty()
        specialty = $('#specialty').val();
        $.ajax({
            url:  '/area/specialty_by_area/'+specialty,
            type:  'get',
            dataType:  'json',
            success: function(data) {
                data.specialty_kind.forEach(function(element) {
                    $('#subSpecialty').append('<option value="'+element.pk+'">'+ element.name +'</option>');
                    });
                }
            });

        })    

    });
