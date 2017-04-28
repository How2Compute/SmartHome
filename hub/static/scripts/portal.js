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
          console.log("Successfully made request!")
        })
        .fail(function() {
          console.log("Failed to update device status!")
        })
    })
    
    $('.on_off_switch').click(function() {
      // Get the device's ID from the button
      deviceID = $(this).attr('data-deviceid')
      // To avoid scope issues with $(this)
      selfObj = $(this)
      // log for debugging purposes
      console.log("Switching " + deviceID + $(this).val());
      $.ajax({
          url: "/update/" + deviceID + "/status/" + $(this).val(),
          type: 'PUT'
        }).done(function() {
          console.log("Successfully made request!")
          value = selfObj.val();
          console.log("Put val() into variable")
          if (value == "ON")
          {
            console.log("Changing text to OFF!")
            selfObj.val("ON")
            selfObj.html('<i class="fa fa-power-off"></i> OFF ')
            selfObj.closest("td").find("#test").text("(currently: ON)")
          }
          else
          {
            console.log("Changing text to ON!")
            selfObj.val("ON")
            selfObj.html('<i class="fa fa-power-off"></i> ON ')
            selfObj.closest("td").find("#test").text("(currently: OFF)")
            console.log("done!")
          }
        })
        .fail(function() {
          console.log("Failed to update device status!")
        })
    })
})