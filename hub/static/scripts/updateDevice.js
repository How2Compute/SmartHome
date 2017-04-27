$('document').ready(function() {
    // Autofocuss on the value field
    $('#myModal').on('shown.bs.modal', function () {
        console.log("selecting...")
        $('#modal_value').focus()
        $('#modal_value').val("TODO_2")
    })
    
    $('#updateModalButton').click(function(e) {
        $('#modal_value').value = "TODO_2"
        console.log("Updating...")
        $('#modal_key').value = "TODO"
    })
    
})