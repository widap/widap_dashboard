FROM jupyterhub/singleuser:0.9
USER root
RUN apt-get update && apt-get install -y libmysqlclient-dev
USER jovyan
RUN conda install matplotlib pandas numpy scipy sqlite ipywidgets mysql seaborn mysql-connector-python
CMD ["jupyterhub-singleuser"]
