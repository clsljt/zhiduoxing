from typing import Any
# import httpx
from mcp.server.fastmcp import FastMCP
import pymysql


mcp = FastMCP("myServer")

@mcp.tool()
async def get_level_depart(name: str) -> str:
    """得到比赛的等级和举办比赛的学院，或者查看比赛是否是学校所认证的

    Args:
        name: the name of competition
    """
    db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='mcp')
    cursor = db.cursor()
    select_sql = "SELECT * from competition where name like '%{}%' ;".format(name)
    cursor.execute(select_sql)
    info = cursor.fetchall()
    db.close()
    if len(info) == 0:
        return "\n---\n没有查到 {} 相关的比赛"
    else:
        res = "查到比赛有\n"
        for i in info:
            res+="{} 为 {} 举办，等级为 '{}' \n".format(i[1],i[2], i[3])
        return "\n---\n学校认证的相关比赛有:"+res
    
@mcp.tool()
async def get_comp(name: str) -> str:
    """通过比赛的等级，返回该等级的比赛

    Args:
        name: 比赛的等级
    """
    db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='mcp')
    cursor = db.cursor()
    select_sql = "SELECT * from competition where level like '%{}%' ;".format(name)
    cursor.execute(select_sql)
    info = cursor.fetchall()
    db.close()
    if len(info) == 0:
        return "\n---\n没有查到 {} 相关的比赛"
    else:
        res = ""
        for i in info:
            res+="{} 的等级是 {}, ".format(i[1], name)
        return "".format(name)+res

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')