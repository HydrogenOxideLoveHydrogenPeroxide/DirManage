import shutil,logging,sys
import json
from pathlib import Path
from pprint import pprint,pformat
import os#os.getcwd()
import jieba.analyse
import re

from JsonReader import relevent_settings,read_settings
"""库默认配置"""
DEBUG=True 
SEPLINE=80#count of -
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
    # logging.disable(logging.DEBUG)
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
    def __init__(self,dirname:str,in_dir:str):
        self.dirname=dirname#文件夹名称
        self.in_dir=in_dir#str
        self.files=[]#文件列表[FILE...]
        self.dirs=[]#文件夹[DIR...]
        
    def add_file(self,file:FILE):
        self.files.append(file)
    
    def add_dir(self,dir):
        self.dirs.append(dir)

    def __call__(self) -> str:
        return pformat(
            {
            "dirname":self.dirname,
            "in_dir":self.in_dir,
            "files":[str(file) for file in self.files],
            "dirs":self.dirs
            }
        ,indent=2)
        
"""功能函数"""
def scan_files(src_folder:str=default_filepath):#扫描文件夹中文件，返回关键词
    logging.info('scaning folder:%s',src_folder)
    #鲁棒性检查
    if not os.path.exists(src_folder):
        raise FileNotFoundError('文件夹不存在')
    
    #功能实现
    # for root, dirs, files in os.walk(src_folder):
        # for dir in dirs:
    #         pass
    #     for file in files:
    #         file_path = str(Path(src_folder)/os.path.join(root, file))#文件路径
    #         file_extend = os.path.splitext(file)[1].lower()#文件后缀
    #         file_name = os.path.splitext(file)[0]

    #         file=FILE(file_name,file_extend,file_path)
            
            
    # if DEBUG:     
    #     with open(FILES_PATH_NAME_EXTEND['name'],'w',encoding=FILES_PATH_NAME_EXTEND['encoding']) as jsonobj:
    #         json.dump(,jsonobj,ensure_ascii=False,
    #                 indent=FILES_PATH_NAME_EXTEND['indent'])
        
if __name__ == "__main__":
    scan_files(r"C:\Users\Administrator\Documents\WeChat Files\wxid_ckaj76sdrypm22\FileStorage")