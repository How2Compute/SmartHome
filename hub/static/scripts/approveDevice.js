// When the document has finished loading
$('document').ready(function() {
    // When a user changed something in a custom_entry field
    $('.approveButton').click(function() {
      var deviceID = $(this).attr('data-deviceid')
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
        })
        .fail(function() {
          $('.alert-danger').css("display", "flex")
          console.log("Failed to update device status!")
        })
    })
})