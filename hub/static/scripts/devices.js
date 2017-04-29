// When the document has finished loading
$('document').ready(function() {
  
    $('#no_results').hide()
    // Check if there are no results when it loads
    if($('.devices_table tbody tr:visible').length == 0)
    {
      console.log("No data!")
      $('#no_results').show()
    }
    
    // When a user changed something in a custom_entry field
    $('.deleteDevice').click(function() {
      var deviceID = $(this).attr('data-deviceid')
      
      // For use within the ajax .done function
      var selfObj = $(this)
      $.ajax({
          url: "/delete/" + deviceID,
          type: 'POST'
        }).done(function() {
          // Hide/Remove the danger box (incase it was still open)
          $('.alert-danger').css("display", "none")
          // Remove the entry from the table (sothat the user does not have to reload the page)
          selfObj.closest("tr").remove()
          
          if($('.devices_table tbody tr:visible').length == 0)
          {
            console.log("No data!")
            $('#no_results').show()
          }
          
          
        })
        .fail(function() {
          $('.alert-danger').css("display", "flex")
          console.log("Failed to update device status!")
        })
    })
})