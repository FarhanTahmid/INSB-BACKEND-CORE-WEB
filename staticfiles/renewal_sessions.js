function searchfunction(){
    let input,filter,table,tr,td,j;
    input=document.getElementById("search");
    filter=input.value.toUpperCase();
    table=document.getElementById("renewal_request_table");
    tr=table.getElementsByTagName("tr");
    
    for(j=0;j<tr.length;j++){
        td=tr[j].getElementsByTagName("td");
        message=document.getElementById("no_data");

        if(td.length > 0){
            if(td[0].innerHTML.toLocaleUpperCase().indexOf(filter)> -1 ||
            td[1].innerHTML.toLocaleUpperCase().indexOf(filter)> -1 ||
            td[2].innerHTML.toLocaleUpperCase().indexOf(filter)> -1 ||
            td[3].innerHTML.toLocaleUpperCase().indexOf(filter)> -1){
            tr[j].style.display="";
            message.innerHTML="";
        }
                else{
                    tr[j].style.display="none";
                }
        
        }        
        if(td.length==0){
            message.innerHTML="Member not found!";
        }
    }
}
let copyText=document.querySelector(".copy-text");
copyText.querySelector("button").addEventListener("click",function(){
    let input =copyText.querySelector("input.text");
    input.select();
    document.execCommand("copy");
    copyText.classList.add("active");
    window.getSelection().removeAllRanges();
    setTimeout(function(){
        copyText.classList.remove("active");
    },3000);
});