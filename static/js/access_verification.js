function verify() {
    do {
        var password = prompt("Please enter your Life_password", "");
        var accessible = false;
        if (password.length <= 20) {
            // $.post("/api/verify", {"password": password}, function(result){
                // if (result['Accessible'] === true)
                //     window.location.replace('/');
                // else{
                //     alert('Password Error.');
                // }
            // }, "json");
            $.ajax({
                url: "/api/verify",
                data: {"password": password},
                dataType: "json",
                async: false,
                type: "POST",
                success: function(result){
                    if (result['Accessible'] === true){
                        accessible = true
                        window.location.replace('/')
                    }
                    else
                        alert('Password Error.');
                },
            })
        }
        else{
            alert("Password is too long.");
        }
    }while(accessible === false);
}
$(document).ready(verify);
