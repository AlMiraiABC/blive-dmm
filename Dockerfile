FROM almirai/python:3.10.4-alpine
LABEL author="almirai"
LABEL email="live.almirai@outlook.com"
LABEL version="0.1"
LABEL description="bilibili live danmaku management."
LABEL name="bilibili-live-dm-manager"
COPY . .
USER root
RUN python -m pip install --no-cache-dir -U -i https://pypi.tuna.tsinghua.edu.cn/simple pip && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
USER appuser
EXPOSE 8080
ENV LOG_LEVEL=info
CMD python app.py
