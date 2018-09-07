### Nonsense

**Problem**

支持pdf功能时，出现了浏览问题，宽度能百分百，
高度很下，即使css设置了100%

**Solution**

将html和body标签及所有父类标签全部设置

    style="height: 100%;

**Problem**

无法加载upload文件夹里的静态资源

**Solution**

    app = Flask(__name__, static_folder='', static_url_path='')
    # static_url_path 默认前缀是 /static
    # static_url_path='', 并不会将资源目录转为根目录，只是修改了映射，实际文件还是在static文件夹里
    # static_folder 修改资源文件夹
    
2018_9_7补充

先前的做法是错误的，将静态文件夹扩充至根目录，虽然方便，但是这样会暴露所有文件，
可以在不进行任何认证的情况下，直接通过url访问网站非公开的静态文件。

解决方案

设置一个视图函数，将访问upload文件夹里的链接导向该视图函数，然后进行enter_required的认证，
最后返回文件，同时消除对static_folder和static_url_path的修改

    @main.route('/upload/<path:file_name>')
    @enter_required
    def view_file(file_name):
        response = make_response(send_from_directory(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], file_name))
        return response

**Problem**

由于最初为了防止文件冲突将上传的文件按照关键信息拼接成了新文件名，
但3元素的文件名中，两元素为用户定义，即用户名和文件名，所以使用正则等手段
从新文件名中切分3元素会产生bug，切分出错。

**Solution**

前后端交互等，应使用三元素交互，需要新文件名，直接使用三元素拼接。
避免只传输新文件名导致的不正确切割，而数据库无法查询到正确的文件。

**Problem**

由于downloader和show_file等文件相关视图函数并没有查询数据库的验证操作，
这会导致可以通过拼接URL访问用户无权访问的文件。

**Solution**

最初想法：
对所有的交互使用三元素，然后在操作之前进行数据库查询，避免出现拼接的操作。

最后的解决方法:
直接使用从后台数据中取出的object id作为request唯一参数。一切操作先进行数据库查询，
约定数据库中有，才进行响应，否则，即使文件存在也不响应。

