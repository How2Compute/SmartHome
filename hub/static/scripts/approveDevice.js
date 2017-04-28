// When the document has finished loading
$('document').ready(function() {
    $('#no_results').hide()
    // Check if there are no results when it loads
    if($('.devices_approve_table tbody tr:visible').length == 0)
    {
      console.log("No data!")
      $('#no_results').show()
    }
    // When a user changed something in a custom_entry field
    $('.approveButton').click(function() {
      var deviceID = $(this).attr('data-deviceid')
      // For use within the ajax .done function
      var selfObj = $(this)
      data = {
        id: deviceID,
        approve: $(this).val() == "approve"
      }
      
      $.ajax({
          url: "/approve",
          type: 'POST',
          data: JSON.stringify(data),
          contentType: "application/json"
        }).done(function() {
          // Hide/Remove the danger box (incase it was still open)
          $('.alert-danger').css("display", "none")
          // Remove the entry from the table (sothat the user does not have to reload the page)
          selfObj.closest("tr").remove()
          
          // Delay a while (as otherwise this proves to be buggy)
          setTimeout(function() {
            if($(document).find('.devices_approve_table tr:visible').length == 0)
          {
            $('#no_results').css("display", "flex")
          }
          }, 1000)
          
          
        })
        .fail(function() {
          $('.alert-danger').css("display", "flex")
          console.log("Failed to update device status!")
        })
    })
})