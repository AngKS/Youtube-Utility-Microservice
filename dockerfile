FROM public.ecr.aws/lambda/python:3.11
COPY requirements.txt .
RUN yum install -y mesa-libGLw
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" 
COPY . ${LAMBDA_TASK_ROOT}
CMD ["app.lambda_handler"]