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

**Solution**（未实现）

对所有的交互使用三元素，然后在操作之前进行数据库查询，避免出现拼接的操作。
