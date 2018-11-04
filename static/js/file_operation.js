function add0(m){return m<10?'0'+m:m}  // 保证时间的格式化

function format(timestamp)  // 将timestamp转化为人类看得懂的时间
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

function delete_each_file(file_id) {
    $.ajax({
        url: "/api/delete",
        data: {"file_id": file_id},
        dataType: "json",
        async: true,
        type: "POST",
        success: function(result) {
            if(result["errno"] == 0) {
                var file_item_tags = $(".file_info");
                for (let index = 0; index < file_item_tags.length; index++) {
                    var element = file_item_tags[index];
                    if (element.getAttribute("file_id") == file_id) {  // 删除已被确认删除的元素
                        element.remove();
                    }
                }
            }
            else {
                alert("Failed to delete.\nError code: " + result["errno"] + "\nError message: " + result["errmsg"]);
            }
        }
    })
}

function delete_files() {  // 删除复选框选中的项
    var input_ = $(".file_checkbox");
    for (let index = 0; index < input_.length; index++) {
        var element = input_[index].checked;
        if (element == true) {
            delete_each_file(input_[index].getAttribute("file_id"));
        }
    }
}
