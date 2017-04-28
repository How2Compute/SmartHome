// When the document has finished loading
$('document').ready(function() {
    $("table").find("[data-deviceid='" + 1 + "']").first().css("color", "red");
    // When a user changed something in a custom_entry field
    $('.custom_entry').change(function() {
      var deviceID = $(this).attr('data-deviceid')
      console.log("Device#: " + deviceID + "!")
      
      $.ajax({
          url: "/update/" + deviceID + "/status/" + $(this).val(),
          type: 'PUT'
        }).done(function() {
          $('.alert-danger').css("display", "none")
          $('.alert-success').css("display", "flex")
        })
        .fail(function() {
          $('.alert-success').css("display", "none")
          $('.alert-danger').css("display", "flex")
          console.log("Failed to update device status!")
        })
    })
    
    // When the ON/OFF button gets pressed
    $('.on_off_switch').click(function() {
      // Get the device's ID from the button
      deviceID = $(this).attr('data-deviceid')
      // To avoid scope issues with $(this)
      selfObj = $(this)
      
      // Request an update for the status key
      $.ajax({
          url: "/update/" + deviceID + "/status/" + $(this).val(),
          type: 'PUT'
        }).done(function() {
          if (selfObj.val() == "ON")
          {
            selfObj.val("ON")
            selfObj.html('<i class="fa fa-power-off"></i> OFF ')
            selfObj.closest("td").find("#test").text("(currently: ON)")
          }
          else
          {
            selfObj.val("ON")
            selfObj.html('<i class="fa fa-power-off"></i> ON ')
            selfObj.closest("td").find("#test").text("(currently: OFF)")
          }
          // Show the bootstrap success alert
          $('.alert-danger').css("display", "none")
          $('.alert-success').css("display", "flex")
        })
        .fail(function() {
          $('.alert-success').css("display", "none")
          $('.alert-danger').css("display", "flex")
          console.log("Failed to update device status!")
        })
    })
})