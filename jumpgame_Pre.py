import pyxel

class Player:
    def __init__(self):
        self.player_x=16#プレイヤーの座標ではなくmapの座標
        self.player_y=48#正真正銘プレイヤーの座標
        #ジャンプ関連
        self.canJump=True#ジャンプができるか
        self.vel=0
        self.acc=1
        self.fallend=False#ジャンプが終了したか
        #クリアフラグ
        self.go=0
        self.cl=0

        self.Y_GROUND=80
        self.ntile=[0,0]
    #プレイヤーが歩く
    def walk(self,Wal):
        #プレイヤーがいる所のタイルを取得
        tile_x = self.player_x / 8
        tile_y = self.player_y / 8
        self.ntile = pyxel.tilemap(0).pget(tile_x, tile_y-2) 
        #下が地面でトラップに触っていないなら歩ける
        if(self.ntile==(0,1) and Wal.stopanim==False):
            if pyxel.btn(pyxel.KEY_RIGHT):
                self.player_x = self.player_x + 2
            if pyxel.btn(pyxel.KEY_LEFT):
                self.player_x = self.player_x - 2
        #スタートより前に戻るのを防止
        if(self.player_x<=16):
            self.player_x=16

    #穴に落ちた時の動き
    def fall(self):
        self.vel=5
        self.vel += self.acc
        self.player_y += self.vel
        #フラグ管理
        self.canJump = False
        self.fallend = True
    def f_update(self,fall_judge):
        #落下が終わっていたら次は落ちない
        #落下判定があった一度だけfall()関数を実行する
        if self.fallend:
            return
        if fall_judge:
            self.fall()

    #ジャンプした時の動き
    def jump(self):
        if self.canJump:
            pyxel.play(0,2,loop=False)
            self.canJump = False
            self.vel = -5
    def j_update(self,wal):
        #ジャンプ可能＝プレイヤーが着地済みの時は落ちない
        if self.canJump:
            return
        self.vel += self.acc
        self.player_y += self.vel
        #穴に落ちている時は地面の判定が違う
        if wal.falling:
            #yが56になるまで落下アニメーション
            if self.player_y >= self.Y_GROUND-24: # 地面についたら
                self.player_y = self.Y_GROUND-24
                self.vel = 0
                self.canJump = True
        else:
            if self.player_y >= self.Y_GROUND-32: # 地面についたら
                self.player_y = self.Y_GROUND-32
                self.vel = 0
                self.canJump = True
                self.fallend=False
                

class GameManager:
    def __init__(self):
        self.wall_y=0
        self.frame=0
        self.record=0
        self.h_score=0
        self.tile = [0, 0]
        self.utile=[0,0]
        self.start=0
        self.falling=False
        self.countDown=0
        self.stopcount=0
        self.stopanim=False

    #天井落下
    def press(self,PL):
        #落下時間管理
        self.frame+=1
        #ゴール時間の記録
        self.record+=1
        #壁の落下アニメーション
        if(self.wall_y+24<=PL.player_y or self.tile==(0,1)):
            if (self.frame>60):
                self.wall_y+=0.5
                if(self.wall_y>32):#繰り返し
                    self.wall_y=0
                    self.frame=0
        else:#player_yが壁位置より高くなる or 頭上のタイルが壁になるとゲームオーバー
            self.stopcount=0
            self.stopanim=False
            PL.go=1
        if(PL.player_x>986):#ゲームクリア条件
            if(self.h_score>self.record or self.h_score==0):#ハイスコア保持
                self.h_score=self.record
            PL.cl=1
    #プレイヤー落下判定
    def Falls(self,PL):
        #プレイヤーのいるmapを取得
        tile_x = (PL.player_x) / 8
        self.tile = pyxel.tilemap(0).pget(tile_x-1, 2)#プレイヤーの頭上タイル
        self.utile = pyxel.tilemap(0).pget(tile_x-1, 5)#プレイヤーの下のタイル
        #落下判定
        if(PL.player_y==48 or PL.player_y==52 or PL.player_y==56):
            if(self.utile==(0,1)):#下が穴だったら
                self.falling=True
            else:
                self.falling=False
                PL.fallend=False #fallend変数をリセット、再度落ちることができるようにする
            
            if(self.utile==(0,2)):#下がトラップだったら
                self.stopanim=True
                if(self.stopanim==True):
                    self.stopcount+=1
                    PL.player_y=56
                    pyxel.play(0,0)
                if(self.stopcount>45):#45フレーム止まる
                    #自動脱出用
                    PL.player_x+=12
                    PL.player_y=48
                    #リセット
                    self.stopcount=0
                    self.stopanim=False

    def s_manager(self,PL):#ゲームリセット
        if pyxel.btnp(pyxel.KEY_S):
            PL.go=0
            PL.cl=0
            PL.player_x=16
            PL.player_y=48
            self.record=0
            self.wall_y=0
            self.frame=0
            self.countDown=1
            self.d_number=3
            pyxel.play(0,1)
        if(self.countDown==1):#スタート時の3秒カウントダウン
            self.frame+=1
            if(self.frame<90):
                if(self.frame%30==0):
                    pyxel.play(0,1)
                    self.d_number-=1
            else:
                self.countDown=2
                self.start=1
                self.frame=0

class App:
    def __init__(self):
        #オブジェクト代入
        self.p=Player()
        self.w=GameManager()

        pyxel.init(160, 80, title="Pyxel Jump")
        pyxel.load("assets/resource.pyxres")
        pyxel.run(self.update, self.draw) 
        

    def update(self):
        #Qでゲーム終了
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        #リスタートを実行
        if(self.w.start==0):
            self.w.s_manager(self.p)
        #ゲームオーバー or ゲームクリア時に他の関数の動きを止める
        if(self.p.go==1 or self.p.cl==1):
            self.w.start=0
            return
        
        if(self.w.start==1):
            self.p.walk(self.w)
            self.p.j_update(self.w)
            self.p.f_update(self.w.falling)
            self.w.Falls(self.p)
            self.w.press(self.p)
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.p.jump()


    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(-self.p.player_x+16,48,0,0,32,1000,32)
        pyxel.bltm(-self.p.player_x+16,self.w.wall_y,0,0,0,1000,24)
        pyxel.blt(8,self.p.player_y,0,8,0,8,8,0)
        if(self.w.stopanim==True):
            pyxel.blt(8,self.p.player_y,0,8,8,8,8,0)

        if(self.w.countDown==1):
            pyxel.text(80,40,str(self.w.d_number),7)
        if(self.w.countDown==0):
            pyxel.text(80,40,"Press S to start",7)
            pyxel.text(80,47,"Space = jump",7)
        if(self.p.cl==1):
            pyxel.text(80,30,"GameClear",10)
            pyxel.text(80,40,"Rec: "+str(self.w.record),7)
            pyxel.text(80,47,"Top: "+str(self.w.h_score),7)
            pyxel.text(80,55,"press S to restart",6)
        if(self.p.go==1):
            pyxel.text(80,40,"GameOver",8)
            pyxel.text(80,45,"press S to restart",7)
        
App()