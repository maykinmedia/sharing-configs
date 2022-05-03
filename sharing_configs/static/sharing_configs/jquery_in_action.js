//enable/disable a button with jq (methods attr,removeAttr)  
// submit button form gets enabled if file field present 
      
(function($){
    $("#id_file_name").change(function(){
        console.log("state input file:",$(this).val())
        if($(this).val()==""){            
            $(".enableOnInput").prop("disabled",true)
        }
        else{            
            $(".enableOnInput").prop("disabled",false)
        }
    }
    )
})(django.jQuery)



