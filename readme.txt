1、新建项目 
    python mamange.py startapp polls，
    并把polls.apps.PollsConfig加入到INSTALLED_APPS 配置中
2、在models中新建模型类，（修改模型类后同步数据库也是这几个步骤）
    1）执行 python manage.py makemigrations polls 会生成迁移文件 polls/migrations/0001_initial.py
        配置数据库是还要在__init__中初始化
            import pymysql
            pymysql.install_as_MySQLdb()
        如果报：django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.3 or newer is required; you have 0.7.11.None
            解决办法：
                找到Python安装路劲下的Python36-32\Lib\site-packages\django\db\backends\mysql\base.py文件将文件中的如下代码注释
                if version < (1, 3, 3):
                    raise ImproperlyConfigured("mysqlclient 1.3.3 or newer is required; you have %s" % Database.__version__)
                注释即可；
        如果报：AttributeError: 'str' object has no attribute 'decode'
            解决方法：
                根据堆栈提示，找到对应文件，修改decode为encode
    
    2）查询迁移文件所执行的sql：python manage.py sqlmigrate polls 0001， 可以显示建表的sql代码
    3）执行迁移文件：python manage.py migrate
3、Django常用模型操作：
    1）参数
        default: 默认
        null ：设置是否为空，针对数据库中该字段是否可以为空
        blank ：设置是否为空，针对表单提交该字段是否可以为空
        primary_key：创建主键
        unique：唯一
    2）操作：
        查询单个数据：first() last() count() exists()
        限制查询集：相当于sql中的limit，模型名.objects.all()[0:5] 小标不能为负数
        字段查询：对sql中的where实现，作为方法filter(),exclude()，get()的参数
            属性名称__比较运算符 = 值
            一对多或多对多关系的可以使用 实体名__属性名__比较运算符，这里的实体名为一的关系；
            
        比较运算符：
            通配符可以使用contains运算符代替，
            exact 相当于等于，iexact忽略大小写的等于
            startswith,istartswith,endswith,iendswith
            isnull，isnotnull：是否为空。filter(name__isnull=True)
            in：是否包含在范围内。filter(id__in=[1,2,3])
            gt，gte，lt，lte：大于，大于等于，小于，小于等于。filter(age__gt=10)
            pk：代表主键，也就是id。filter(pk=1)
        聚合函数：ggregate()函数返回聚合函数的值，Avg，Count，Max，Min，Sum
            Student.objects.aggregate(Max('age'))
        F对象：可以使用模型的A属性与B属性进行比较
            Grade.objects.filter(girlnum__gt=F('boynum'))：统计女生数大于男生数的班级
            F对象支持算数运算：Grade.objects.filter(girlnum__gt=F('boynum') + 10)
        Q对象：就是为了将过滤条件组合起来，符号&或者|将多个Q()对象组合起来传递给filter()，exclude()，get()等函数，
            Student.objects.filter(~Q(age=12) | Q(name='张三'))
        
    3）模型的对应关系：定义模型时指定 
        models.CASCADE                      默认值
        models.PROTECT                  保护模式
        models.SET_NULL                 置空模式
        models.SET_DETAULT          置默认值
        models.SET()     删除的时候吃重新动态指向一个实体访问对象元素

        OneToOneField：stu = models.OneToOneField(Student，[on_delete.CASCADE])
        多对一：ForeignKey ，s_grade = models.ForeignKey(Grade, on_delete=PROTECT)//班级与学生的对应关系
            通过一获取多的数据：一的对象.多的模型_set，然后在获取数据all(), get(), filter() 等等
            获取班级的学生(通过一获取多)
            ...
                1\. 低性能方法：
                g = Grade.objects.all().first()
                s = Student.objects.filter(s_grade=g)

                2\. 高性能方法：
                g = Grate.objects.all().first()
                s = g.student_set.all()
        ManyToManyField:生成表的时候会多生成一张表（实际会有三张表）,生成的表是专门用来维护关系的,生成的表是使用两个外键来维护多对多的关系
            获取指定商品的购买者信息：
                ...
                    g = Goods.objects.filter(id=1)[0]
                    g.g_user.all()
                ...
            添加额外的属性字段，可以考虑建立一张中间表；
    
4、模板
    1）抛出404：raise Http404("Question does not exist")，一个快捷函数，可以不用捕获异常
        from django.shortcuts import get_object_or_404
        ...
        question = get_object_or_404(Question, pk=question_id)
        类似的还有get_list_or_404，
    2）取值：模板里可以使用.号取值：首先 Django 尝试对对象使用字典查找（也就是使用 obj.get(str) 操作），如果失败了就尝试属性查找（也就是 obj.str 操作），结果是成功了。如果这一操作也失败的话，将会尝试列表查找（也就是 obj[int] 操作）
        也可以调用对象方法：{% for choice in question.choice_set.all %}

    3）去除硬编码url：可以使用 {% url %} 标签代替它
        <li><a href="{% url 'detail' question.id %}">{{ question.question_text }}</a></li>
        detail为urls.py里定义的路由参数name属性指定值
    4）为url加上命名空间：在urls.py中加上app_name = 'polls'的语句即可，同时软编码的url值应该加上命名空间，
        {% url 'polls:detail' question.id %}

    5）使用通用视图：Django 提供一种快捷方式，叫做“通用视图”系统，根据 URL 中的参数从数据库中获取数据、载入模板文件然后返回渲染后的模板，
        通用视图将常见的模式抽象化，可以使你在编写应用时甚至不需要编写Python代码；
        ① 转换 URLconf
            path('', views.IndexView.as_view(), name='index'),
            path('<int:pk>/', views.DetailView.as_view(), name='detail'),
            path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),

        ② 删除一些旧的、不再需要的视图，每个通用视图需要知道它将作用于哪个模型。 这由 model 属性提供。
            DetailView 期望从 URL 中捕获名为 "pk" 的主键值，所以我们为通用视图把 question_id 改成 pk
            默认情况下，通用视图 DetailView 使用一个叫做 <app name>/<model name>_detail.html 的模板
            在我们的例子中，它将使用 "polls/question_detail.html" 模板
            template_name 属性是用来告诉 Django 使用一个指定的模板名字，而不是自动生成的默认名字
            对于 ListView， 自动生成的 context 变量是 question_list。为了覆盖这个行为，我们提供 context_object_name 属性，表示我们想使用 latest_question_list。
            
            from django.views import generic
            class IndexView(generic.ListView):
                template_name = 'polls/index.html'
                context_object_name = 'latest_question_list'

                def get_queryset(self):
                    """Return the last five published questions."""
                    return Question.objects.order_by('-pub_date')[:5]
            class DetailView(generic.DetailView):
                model = Question 
                template_name = 'polls/detail.html'
        ③ 基于 Django 的通用视图引入新的视图

5、静态资源的引入：静态资源将利用STATICFILES_FINDERS指定的搜索器搜索路径下面的STATIC_URL指定目录。STATICFILES_FINDERS默认依次包含：
        FileSystemFinder：在文件系统里搜索STATICFILES_DIRS指定目录。默认不包含任何目录
        AppDirectoriesFinder：搜索INSTALLED_APPS注册过的应用目录
    因此，使用入门级配置的正常情况下就是在project注册app，然后在app目录下存放static目录,或通过STATICFILES_DIRS参数
    指定
        STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

6、模型层的详细操作：
    1）字段选项： 
        max_length（varchar),
        null,
        blank, null 选项仅仅是数据库层面的设置，然而 blank 是涉及表单验证方面。如果一个字段设置为 blank=True ，在进行表单验证时，接收的数据该字段值允许为空，而设置为 blank=False 时，不允许为空。
        choices,接收一个可迭代的列表或元组（基本单位为二元组）。如果指定了该参数，在实例化该模型时，该字段只能取选项列表中的值。
            每个二元组的第一个值会储存在数据库中，而第二个值将只会用于显示作用,使用 get_xxx_display() 方法获取显示名
            class Person(models.Model):
                SHIRT_SIZES = (
                    ('S', 'Small'),
                    ('M', 'Medium'),
                    ('L', 'Large'),
                )
                name = models.CharField(max_length=60)
                shirt_size = models.CharField(max_length=1, choices=SHIRT_SIZES)      
        default，
        help_text，
        primary_key，主键字段是只可读的，如果你修改一个模型实例该字段的值并保存，你将等同于创建了一个新的模型实例
        unique，
        db_column，
        db_index，If True, a database index will be created for this field.
        editable，If False, the field will not be displayed in the admin or any other ModelForm. They are also skipped during model validation. Default is True.
        error_messages，The error_messages argument lets you override the default messages that the field will raise
        unique_for_date，Set this to the name of a DateField or DateTimeField to require that this field be unique for the value of the date field
    1.1）域类型：AutoField BigAutoField BigIntegerField BinaryField BooleanField CharField DateField
            DateTimeField DecimalField DurationField EmailField FileField FilePathField FloatField 
            ImageField IntegerField GenericIPAddressField NullBooleanField PositiveIntegerField 
            PositiveSmallIntegerField SlugField SmallIntegerField TextField TimeField URLField UUIDField 
    2）备注名：除了 ForeignKey ， ManyToManyField 和 OneToOneField ，任何字段类型都接收一个可选的参数 verbose_name ，如果未指定该参数值， Django 会自动使用该字段的属性名作为该参数值，并且把下划线转换为空格
        first_name = models.CharField("person's first name", max_length=30)
    3）Meta选项：
        abstract
        app_label
        base_manager_name
        db_table
        ordering
        indexes
        unique_together
    4）模型继承：？？
    5）域属性及方法：？？
    6）queryset：当执行如下操作时会导致数据库操作，迭代、切片、Pickling、调用repr()，len()，list()、执行判断布尔值时、
        返回QuertSet的常用操作：
            filter,exclude,order_by,,none
            annotate
        QuerySEt的方法并返回QuerySet：
            distinct,
            values：不返回模型，将模型json化，可以用参数指定返回哪些字段，同时字段可以使用上面那些如filter的操作；
            values_list：返回元祖的列表，没有列名信息
            union：
            prefetch_related：？
            extra：extra(select=None, where=None, params=None, tables=None, order_by=None, select_params=None)
                select 参数可以让你在 SELECT 从句中添加其他字段信息。它应该是一个字典，存放着属性名到 SQL 从句的映射
                    	Entry.objects.extra(select={'is_recent': "pub_date > '2006-01-01'"})
                        结果中每个 Entry 对象都有一个额外的 is_recent 属性，它是一个布尔值
                        Blog.objects.extra(select={'entry_count': 'SELECT COUNT(*) FROM blog_entry WHERE blog_entry.blog_id = blog_blog.id'},)
                select_params 可能想给 extra(select=...) 中的 SQL 语句传递参数，这时就可以使用 select_params 参数，使用%s的形式
                where 显示定义 SQL 中的 WHERE 从句，接受字符串列表做为参数，所有的 where 参数彼此之间都是 "AND" 关系。
                    	Entry.objects.extra(where=['id IN (3, 4, 5, 20)'])
                        Entry.objects.extra(where=["foo='a' OR bar = 'a'", "baz = 'a'"])
                tables 手动地给 SQL FROM 从句添加其他表
                order_by 可以是 model 原生的字段名，也可以是 table_name.column_name 这种形式，或者是你在 extra() 的 select 中所定义的字段
                    q = q.extra(order_by = ['-is_recent'])
            defer：跳过某些字段。
            only：只查询某些字段
            select_for_update
            raw：使用原生sql，返回RawQuerySet，可以迭代
        QuerySEt 可以使用操作符
            & Model.objects.filter(x=1) & Model.objects.filter(y=2)
            | Model.objects.filter(x=1) | Model.objects.filter(y=2)
        不返回queryset的方法：
            get_or_create 返回一个元祖（object, created），object为查询或新建的模型，created返回是否为新建
            update_or_create 和上面类似
            bulk_create 
            count

6、视图层
    1）Path转换器：str,int,slug(短横线连接的字符串),uuid,path
        /articles/2003/03/building-a-django-site/
        path('articles/<int:year>/<int:month>/<slug:slug>/', views.article_detail)
        可以自定义转换器
            必须含有如下属性和方法
                class FourDigitYearConverter:
                    regex = '[0-9]{4}'
                    def to_python(self, value):
                        return int(value)
                    def to_url(self, value):
                        return '%04d' % value
            然后
                register_converter(converters.FourDigitYearConverter, 'yyyy')
                path('articles/<yyyy:year>/', views.year_archive),
    2）正则表达式：使用re_path， (?P<name>pattern)
        re_path(r'^comments/(?:page-(?P<page_number>\d+)/)?$', comments),
    3）在视图处理函数指定默认值
    4）include 可以包含其他urls模块，也可直接包含path
        path('<page_slug>-<page_id>/', include([
            path('history/', views.history),
            path('edit/', views.edit),
            path('discuss/', views.discuss),
            path('permissions/', views.permissions),
        ])),
    5）path函数可以加一个字典参数，在视图里可以通过参数捕获
    6）快捷函数
        render：render(request, template_name, context=None, content_type=None, status=None, using=None)
        redirect
    7）装饰器：
        @require_http_methods(["GET", "POST"])
        require_GET()
        require_POST()
        require_safe() accepts the GET and HEAD methods
    8）内置视图：
        serve：可用于为您给的任何目录提供服务
            from django.views.static import serve
            if settings.DEBUG:
                urlpatterns += [
                    re_path(r'^media/(?P<path>.*)$', serve, {
                        'document_root': settings.MEDIA_ROOT,
                    }),
                ]
            可以使用URL帮助函数static() 
            urlpatterns = [
                # ... the rest of your URLconf goes here ...
            ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        404：您在根模板目录中创建了404.html模板可以替换掉系统默认的。request_path，exception是传递给模板的参数；
            404视图传递一个RequestContext并且可以访问模板上下文处理器提供的变量（例如MEDIA_URL）；
            如果DEBUG设置为True（在您的设置文件中），那么将永远不会使用您的404视图，而是会显示您的URLconf以及一些调试信息。
        500：同样的，在根模板目录中创建500.html模板，则加载并呈现模板，默认的500视图不会将任何变量传递给500.html模板标签，需要小心跨站点请求伪造；
        403：模板上下文包含exception，它是触发视图的异常的字符串表示形式。
        400：表示错误条件是客户端操作的结果，
    9）Request 对象，是只读的，
        属性：
            schema（(http or https usually)）
            body 一般为二进制字符串，若是处理表单数据，使用POST属性
            path 不包含scheme和domain的全路径 /music/bands/the_beatles/
            method，encoding，content_type，content_params，GET，POST，COOKIES，
            FILES 类dict对象，key为<input type="file" name="">的name，value为 UploadedFile 对象
            META 包含所有HTTP请求头的字典
            resolver_match
            current_app
            urlconf
            session
            user
        方法：
            get_host get_port get_full_path
            build_absolute_uri
            is_secure
            is_ajax
            read readline readlines __iter__
        QueryDict 对象： GET and POST 属性是个QueryDict的实例，是一个不可变的， QueryDict.copy()可获得可变对象
            QueryDict.__init__(query_string=None, mutable=False, encoding=None)
                >>> QueryDict('a=1&a=2&c=3')
                <QueryDict: {'a': ['1', '2'], 'c': ['3']}>
            QueryDict.fromkeys(iterable, value='', mutable=False, encoding=None)
                >>> QueryDict.fromkeys(['a', 'a', 'b'], value='val')
                <QueryDict: {'a': ['val', 'val'], 'b': ['val']}>
            __getitem__(key) 
                通过[]索引将获得最后一个值（若是多值的话）
            get(key, default=None) 效果同__getitem__
            items() values() 均只返回最后一个
            getlist(key, default=None)
            appendlist(key, item)
            lists() 和 items()对立
            pop(key)
             



100、常用
    1）forloop.counter 指示 for 标签已经循环多少次；
    2）所有针对内部 URL 的 POST 表单都应该使用 {% csrf_token %} 模板标签，需要小心跨站点请求伪造；
        <form action="{% url 'polls:vote' question.id %}" method="post">
            {% csrf_token %}
            ...
    3）request.POST 是一个类字典对象，如果在 request.POST['choice'] 数据中没有提供 choice ， POST 将引发一个 KeyError 
    4）重定向HttpResponseRedirect： 只接收一个参数：用户将要被重定向的 URL，使用 reverse() 函数，这个函数避免了我们在视图函数中硬编码 URL。它需要我们给出我们想要跳转的视图的名字和该视图所对应的 URL 模式中需要给该视图提供的参数
        HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    5）模型的比较：用==比较两个模型，默认会比较主键是否相等；
        复制模型实例：只需要把模型实例的主键设置为None，即可复制；
        一次更新多个对象：
            Entry.objects.filter(pub_date__year=2007).update(headline='Everything is the same')
            Entry.objects.all().update(blog=b)
            只能用于设置非关系域或外键
        一对多关系的模型：
            一查多model_set()，返回的对象还支持add，create，remove，clear，set，
            多查一select_related()：连接查询
    6）xx.objects.create方法，创建一个模型并save；



