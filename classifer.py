import jieba.analyse
import logging,os,shutil
from JsonReader import read_settings
from pathlib import Path
from pprint import pformat
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

"""库默认配置"""
DEBUG=True 
SEPLINE=80 #count of -
CONFIGGILE='config.json'#配置文件,settings
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(message)s",level=logging.DEBUG)

"""配置读取"""
default_filepath,FILES_PATH_NAME_EXTEND=read_settings(CONFIGGILE)
logging.disable(logging.CRITICAL)
logging.info("默认文件夹为%s",default_filepath)
logging.info("临时扫描文件结果储存文件夹%s",FILES_PATH_NAME_EXTEND)
logging.info('debug=%s',DEBUG)
logging.disable(logging.DEBUG)

"""基础函数和类"""
def extract_keywords(text,topK=None):#提取文件名的关键词，便于后期分类
    """_summary_

    Args:
        text (str): 一段文本
        topK (int): 关键词的数量

    Returns:
        list:关键词
    """
    
    logging.disable(logging.CRITICAL)
    keywords = jieba.analyse.extract_tags(text, topK=topK)
    logging.info("\n提取文本%s\n得到关键词%s\n"+"-"*SEPLINE,text,keywords)
    logging.disable(logging.CRITICAL)
    return keywords

class FILE:#文件对象
    def __init__(self,filename:str,fileextend:str,filepath:str):
        realfilepath=Path(filepath)/(filename+fileextend)
        if os.path.exists(realfilepath):#需要保证文件存在保证有效性
            self.file_name=filename
            self.file_extend=fileextend
            self.file_path=filepath
            self.keyword =extract_keywords(self.file_name)
        else:
            raise FileNotFoundError(f'文件 {realfilepath} 不存在')
        
    def update_path(self,newpath)->None:#会更新文件位置，同时
        if isinstance(newpath,str):newpath=Path(newpath)
        elif isinstance(newpath,Path):newpath=newpath
        else:raise TypeError('newpath只能是str和Path')
        
        newpath/=(self.file_name+self.file_extend)
        if not os.path.exists(newpath):
            shutil.move(Path(self.file_path)/(self.file_name+self.file_extend), newpath)
            self.file_path=str(newpath)
        else:
            raise FileExistsError(f'文件{newpath}已经存在')
    
    def copy_to_certain_path(self,newpath)->None:#复制文件到新的位置，原文件不动
        if isinstance(newpath,str):newpath=Path(newpath)
        elif isinstance(newpath,Path):newpath=newpath
        else:raise TypeError('newpath只能是str和Path')
        
        newpath/=(self.file_name+self.file_extend)
        if not os.path.exists(newpath):
            shutil.copyfile(Path(self.file_path)/(self.file_name+self.file_extend), newpath)
            self.file_path=str(newpath)
        else:
            raise FileExistsError(f'文件{newpath}已经存在')
    
    def is_the_dir(self)->list:#在文件夹层级别里面
        dirlist=self.file_path.split('\\')
        # print(dirlist)
        return dirlist
    
    def __call__(self):#返回文件信息的字典
        return {
                    'file_name':self.file_name,
                    'file_extend':self.file_extend,
                    'file_path':str(self.file_path),
                    'keyword':self.keyword
                }

    def __str__(self) -> str:
        return f"文件名{self.file_name+self.file_extend},文件在{self.file_path}"

class DIR:#文件夹对象
    def __init__(self,dirname:str,dirpath:str):
        self.dirname=dirname#文件夹名称
        self.dirpath=dirpath#str
        self.files=[]#文件列表[FILE...]
        
    def add_file(self,file:FILE):
        self.files.append(file)
    
    def __call__(self) -> str:
        return pformat(
            {
            "dirname":self.dirname,
            "in_dir":self.dirpath,
            "files":[str(file) for file in self.files]
            }
        ,indent=2)
 
"""运用的函数"""   
keywordset=set()    

def scan_folder(src_folder=default_filepath):
    logging.info('scaning folder:%s',src_folder)
    #鲁棒性检查
    if not os.path.exists(src_folder):
        raise FileNotFoundError('文件夹不存在')
    
    #功能
    global keywordset
    
    MAINDIR=DIR(src_folder.split('\\')[-1],src_folder)
    Keywordset=set()
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            file_path = str(Path(src_folder)/root)
            file_extend = os.path.splitext(file)[1].lower()#文件后缀
            file_name = os.path.splitext(file)[0]
            # for keyword in extract_keywords(file_name):
                # print(keyword)
            Keywordset.add(file_name)
            MAINDIR.files.append(FILE(file_name,file_extend,file_path))
    # print(MAINDIR())
    return MAINDIR
            
def KMeans_classifier():
    global keywordset
    # print(keywordset)
    # 给定的关键词列表
    keywords=list(keywordset)
    
    # 将关键词转换为向量表示
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(keywords)

    # 使用K-means聚类算法进行分类
    k = 5  # 分成2类，可以根据需要调整
    kmeans = KMeans(n_clusters=k,n_init='auto')
    kmeans.fit(X)

    # 输出各个关键词及对应的类别
    for i, keyword in enumerate(keywords):
        print(f"关键词: {keyword}  类别: {kmeans.labels_[i]}")

if __name__=="__main__":
    scan_folder(r"G:\SPECIAL")
    KMeans_classifier()