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
3、Django模型操作：
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
            
        比较运算符：
            通配符可以使用contains运算符代替，
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
        一对多：ForeignKey ，s_grade = models.ForeignKey(Grade, on_delete=PROTECT)//班级与学生的对应关系
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







100、常用
    1）forloop.counter 指示 for 标签已经循环多少次；
    2）所有针对内部 URL 的 POST 表单都应该使用 {% csrf_token %} 模板标签，需要小心跨站点请求伪造；
        <form action="{% url 'polls:vote' question.id %}" method="post">
            {% csrf_token %}
            ...
    3）request.POST 是一个类字典对象，如果在 request.POST['choice'] 数据中没有提供 choice ， POST 将引发一个 KeyError 
    4）重定向HttpResponseRedirect： 只接收一个参数：用户将要被重定向的 URL，使用 reverse() 函数，这个函数避免了我们在视图函数中硬编码 URL。它需要我们给出我们想要跳转的视图的名字和该视图所对应的 URL 模式中需要给该视图提供的参数
        HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    5）



