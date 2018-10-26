function add0(m){return m<10?'0'+m:m}
function format(timestamp)
{
    var time = new Date(timestamp * 1000);
    var y = time.getFullYear();
    var m = time.getMonth()+1;
    var d = time.getDate();
    var h = time.getHours();
    var mm = time.getMinutes();
    var s = time.getSeconds();
    return y+'-'+add0(m)+'-'+add0(d)+' '+add0(h)+':'+add0(mm)+':'+add0(s);
}

function modify_time() {
    tmp = $(".upload_time");
    for(i = 0; i < tmp.length; i++){
        tmp[i].innerHTML = format(tmp[i].getAttribute('upload_time'));
    }
}
$(document).ready(modify_time);
