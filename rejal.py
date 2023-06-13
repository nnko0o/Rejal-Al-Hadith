import re
import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List, Any

class Mfeed:

    def __init__(self)-> None:
        self.session = None

    @property
    def Client(self)-> httpx.AsyncClient:
        if self.session:
            return self.session
        else:
            self.session = httpx.AsyncClient(cookies={'__utmc':'1',},)
            return self.session

    def get_id_from_loop_text(self, text: str)-> str:
        length = len(text)
        if length % 3 == 0:
            pattern_length = int(length / 3)
            pattern = text[:pattern_length]

            return pattern
        else:
            print("The string length is not divisible by 3.")

    async def get(
        self,
        url:str,
        ) -> httpx.Response:
        try:
            res = await self.Client.get(url=url,)
            if res.status_code != 200:
                return res.status_code
            return res

        except httpx.TimeoutException:
            res = await self.Client.get(url=url,)
            if res.status_code != 200:
                return res.status_code
            return res
    
    def op(self,path:str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            if f.readable():
                d = f.read()
            else:
                raise ValueError(f"The File `{path}` his Type Not Readable!")
        return d

    async def GET_PAGE_DATA(
        self,
        url:str,
    )-> List[str]:
        res = await self.get(url=url,)
        if isinstance(res, int):
            return {'error':True,'msg':"SCNOK"} # Status Codes Not OK(200)
        
        self.soup = BeautifulSoup(res.content, "html.parser",)
        TextDiv = self.soup.find('div', class_='text')
        # <span class="index index-14451" title="علي بن الحسين" onclick="indexShow('14451');">علي بن الحسين</span>
        lines = TextDiv.text.strip().split('\n')
        print(len(lines))
        result = await self.fix_text(lines)
        return result

    async def fix_text(
        self,
        list_: List[str]
      )-> List[str]:
        line_pattren1 = r'^(\d+) - (\d+) - (\d+) - (.*?)$' # 154 - 154 - 154 - (Text)
        line_pattren2 = r'^(\d+) - (.*?)$' # 153153153 - (Text)

        result_list = []
        for line in list_:
            if re.match(line_pattren1, line):
                result_list.append(line)

            elif re.match(line_pattren2, line):
                unifx_part:list = list(line.split()[0]) # 1, 2, 3,   1, 2, 3,   1, 2, 3.
                id = self.get_id_from_loop_text(line.split()[0]) # 123123123 -> 123

                for i in [ 
                    len(id), # 123><123123
                    (len(id)*2)+1, # 123123><123
                ]: unifx_part.insert(i, ' - ') # add ' - ' for the text
                new_text_part = ''.join(unifx_part) # make it a plain str text
                # Add/Replace it on the line text
                fixed_line = line.replace(line.split()[0], new_text_part) # 123123123 -> 123 - 123 - 123

                print(new_text_part)
                result_list.append(fixed_line)

            else:
                # TODO: Make This part mark this line for use it in the pev page
                print('NOT MATCHED!')


        return result_list

async def main()-> None :
    c = Mfeed()
    r = await c.GET_PAGE_DATA(
        url='http://shiaonlinelibrary.com/%D8%A7%D9%84%D9%83%D8%AA%D8%A8/3021_%D8%A7%D9%84%D9%85%D9%81%D9%8A%D8%AF-%D9%85%D9%86-%D9%85%D8%B9%D8%AC%D9%85-%D8%B1%D8%AC%D8%A7%D9%84-%D8%A7%D9%84%D8%AD%D8%AF%D9%8A%D8%AB-%D9%85%D8%AD%D9%85%D8%AF-%D8%A7%D9%84%D8%AC%D9%88%D8%A7%D9%87%D8%B1%D9%8A/%D8%A7%D9%84%D8%B5%D9%81%D8%AD%D8%A9_764'

    )

# TODO: make code thats get raoi from pev page / nex page

if __name__=='__main__':
    asyncio.get_event_loop(
    ).run_until_complete(
        main()
    )
