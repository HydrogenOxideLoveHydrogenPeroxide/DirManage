import json,os,logging
from pathlib import Path

# logging.basicConfig(format="%(asctime)s-%(levelname)s-%(message)s",level=logging.DEBUG)
# logging.disable(logging.CRITICAL)
def relevent_settings(Dict:dict,Keyword,Condition:str='not null',default=None,*args, **kwargs)->any:#读取相关配置
    """
        Dict:需要提取的字典
        Keyword:字典需要提取的键，
        Condition:字典[KeyWord]对于的值需要满足的条件不同条件用and,or连接，否则返回default
            {
                "not null":非空,
                "int|str|float|list|dict":满足的数据类型
            }
        default:默认返回（null或者不满足Condition）
    """
    value=Dict.get(Keyword,None)
    if Condition:
        Conditions=Condition.lower().split('or')
        if ("not null" in Conditions) and value==None:
            return default
    return value

def read_settings(filename):
    try:
        with open(filename,'r') as config:
            configDict=json.load(config)
            default_filepath=relevent_settings(Dict=configDict,Keyword='default_path',Condition='not Null',default=os.getcwd())
            FILES_PATH_NAME_EXTEND=relevent_settings(configDict,Keyword="temp_file_path_name_extend_keyword",Condition=None,default=None)#用来存扫描文件相关结果
            FILES_PATH_NAME_EXTEND["name"]=str(Path(os.getcwd())/FILES_PATH_NAME_EXTEND["name"])
        return default_filepath,FILES_PATH_NAME_EXTEND
    except FileNotFoundError:#文件读取发生错误
        logging.info(f"Error Occurred in file '{filename}'",exc_info=True)
        try:
            input('按任意键退出')
        except:
            pass
        finally:
            exit()