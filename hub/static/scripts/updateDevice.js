// When the document has finished loading
$('document').ready(function() {
    // allow a button outside of the form to save
    $('#saveButton').click(function () {
        // Grab the new value and the key from the HTML (form)
        var newValue = $('#exampleModal').find('.modal-body input').val();
        var key = $('#saveButton').attr('data-key')
        
        $.ajax({
        // TODO replace 2 with device id
          url: "/update/2/"+ key +"/" + newValue,
          type: 'PUT'
        }).done(function() {
          console.log("Successfully made request!")
          /*
          // adapted from: http://stackoverflow.com/a/6135710
          // Finds the table row for the key we just updated
          var valueField = $(".keyField").filter(function() {
            return $(this).text() == "foo";
          }).closest(".valueField");
          
          valueField.val(newValue)
          */
          // adapted from: http://stackoverflow.com/a/18952083
          // Finds the table row for the key we just updated
          var valueField = $(".keyField").filter(function() {
            return $(this).attr('data-key') == "access_level";
          }).closest(".valueField");
          
          console.log(valueField.val())
          
          //tableRow.css("background-color", "green")
          $('#exampleModal').modal("hide")
        });
        
    })
    // When the modal is shwon
    $('#exampleModal').on('show.bs.modal', function (event) {
      // Get the caller 
      var button = $(event.relatedTarget)
      // Retrieve key and value data
      var key = button.data('key')
      var value = button.data('value')
      
      // Store a reference to the modal in a variable
      var modal = $(this)
      // Find the modals' title
      modal.find('.modal-title').text('Update ' + key)
      // Find the modals' input field
      var valueField = modal.find('.modal-body input')
      // Set the input field to the current value and make it the selected object
      valueField.val(value)
      valueField.focus()
      
      // Find the modals' key field and set it to the key of the thing we want to update
      modal.find('.modal-footer #saveButton').attr('data-key', key)
      
    })
})