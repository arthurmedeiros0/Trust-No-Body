"""Editor Unicode de papel: posições de cursor, linhas visuais e navegação."""
import pygame

class NoteEditor:
    LINE=30
    def __init__(self,font):
        self.font=font
        self.preferred_x=None

    def positions(self,text,area):
        # As linhas quebram em espaços quando possível; palavras longas também cabem.
        positions=[];start=0;y=area.y
        while start<len(text):
            end=start;x=area.x;last_space=None
            while end<len(text) and text[end]!='\n':
                width=self.font.size(text[end])[0]
                if x+width>area.right-8 and end>start:break
                x+=width
                if text[end]==' ':last_space=end
                end+=1
            newline=end<len(text) and text[end]=='\n'
            if not newline and end<len(text) and last_space is not None and last_space>=start:
                end=last_space+1
            x=area.x
            for i in range(start,end):
                positions.append((i,x,y));x+=self.font.size(text[i])[0]
            if newline:
                positions.append((end,x,y));end+=1
            start=end;y+=self.LINE
        if not text or text.endswith('\n'):positions.append((len(text),area.x,y if text else area.y))
        else:
            i,x,last_y=positions[-1]
            x+=self.font.size(text[i])[0]
            if x>area.right-8:x=area.x;last_y+=self.LINE
            positions.append((len(text),x,last_y))
        return positions

    def vertical(self,positions,cursor,direction):
        _,x,y=positions[cursor]
        if self.preferred_x is None:self.preferred_x=x
        target=y+direction*self.LINE
        rows=[p for p in positions if p[2]==target]
        return min(rows,key=lambda p:abs(p[1]-self.preferred_x))[0] if rows else cursor

    def key(self,text,cursor,key,area):
        positions=self.positions(text,area)
        if key in (pygame.K_UP,pygame.K_DOWN):
            return text,self.vertical(positions,cursor,-1 if key==pygame.K_UP else 1)
        self.preferred_x=None
        if key==pygame.K_BACKSPACE and cursor:return text[:cursor-1]+text[cursor:],cursor-1
        if key==pygame.K_DELETE:return text[:cursor]+text[cursor+1:],cursor
        if key==pygame.K_LEFT:return text,max(0,cursor-1)
        if key==pygame.K_RIGHT:return text,min(len(text),cursor+1)
        if key in (pygame.K_HOME,pygame.K_END):
            row=positions[cursor][2];indices=[p[0] for p in positions if p[2]==row]
            return text,min(indices) if key==pygame.K_HOME else max(indices)
        if key==pygame.K_RETURN:return text[:cursor]+'\n'+text[cursor:],cursor+1
        return text,cursor
