#使用基础映像
FROM python:3.8

# 设置环境变量，可以根据需要进行修改
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV BOT_ID 1

ENV DB_HOST host.docker.internal
ENV DB_PORT 3306
ENV DB_USER root
ENV DB_PASSWORD 1
ENV DB_NAME bot

ENV MINIO_ACCESS_KEY weops
ENV MINIO_SECRET_KEY CwWeOps2022
ENV MINIO_HOST paas.weops.com
ENV MINIO_EXTERNAL_ENDPOINT_USE_HTTPS False

# 创建工作目录并设置为工作目录
WORKDIR /app

# 复制项目代码到容器中的工作目录
COPY . /app/

# 安装项目依赖项，可以根据你的项目使用 pip 或 pipenv
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 运行 Django 应用程序，可以根据需要修改
CMD ["python", "manage.py", "my_database_export"]
