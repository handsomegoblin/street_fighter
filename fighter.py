import pygame
import time

class Fighter():
  def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
    self.player = player
    self.size = data[0]
    self.image_scale = data[1]
    self.offset = data[2]
    self.flip = flip
    self.animation_list = self.load_images(sprite_sheet, animation_steps)
    self.action = 0#0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
    self.frame_index = 0
    self.image = self.animation_list[self.action][self.frame_index]
    self.update_time = pygame.time.get_ticks()
    self.rect = pygame.Rect((x, y, 80, 180))
    self.vel_y = 0
    self.running = False
    self.jump = False
    self.attacking = False
    self.attack_type = 0
    self.attack_cooldown = 0
    self.attack_sound = sound
    self.hit = False
    self.health = 100
    self.alive = True


  def load_images(self, sprite_sheet, animation_steps):
    #從精靈表中擷取影像
    animation_list = []
    for y, animation in enumerate(animation_steps):
      temp_img_list = []
      for x in range(animation):
        temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
        temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
      animation_list.append(temp_img_list)
    return animation_list


  def move(self, screen_width, screen_height, surface, target, round_over):
    SPEED = 10
    GRAVITY = 2
    dx = 0
    dy = 0
    self.running = False
    self.attack_type = 0

    #取得按鍵
    key = pygame.key.get_pressed()

    #如果目前沒有攻擊，則只能執行其他操作
    if self.attacking == False and self.alive == True and round_over == False:
      #check player 1 controls
      if self.player == 1:
        #movement
        if key[pygame.K_a]:
          dx = -SPEED
          self.running = True
        if key[pygame.K_d]:
          dx = SPEED
          self.running = True
        #jump
        if key[pygame.K_w] and self.jump == False:
          self.vel_y = -30
          self.jump = True
        #攻擊
        if key[pygame.K_r] or key[pygame.K_t]:
          self.attack(target)
          #確定使用了哪種攻擊類型
          if key[pygame.K_r]:
            self.attack_type = 1
          if key[pygame.K_t]:
            self.attack_type = 2





    #施加重力
    self.vel_y += GRAVITY
    dy += self.vel_y

    #確保玩家停留在螢幕上
    if self.rect.left + dx < 0:
      dx = -self.rect.left
    if self.rect.right + dx > screen_width:
      dx = screen_width - self.rect.right
    if self.rect.bottom + dy > screen_height - 110:
      self.vel_y = 0
      self.jump = False
      dy = screen_height - 110 - self.rect.bottom

    #確保玩家面對面
    if target.rect.centerx > self.rect.centerx:
      self.flip = False
    else:
      self.flip = True
    #應用攻擊冷卻時間
    if self.attack_cooldown > 0:
      self.attack_cooldown -= 1


    #更新玩家位置
    self.rect.x += dx
    self.rect.y += dy
    

  def computer_control(self, screen_width, screen_height, surface, target, round_over):
      dx = 0
      dy = 0
      ATTACK_RANGE = 100  # 修改为适当的攻击范围
      GRAVITY = 2
      SPEED = 5  # 修改为适当的速度
      self.running = False
      self.attack_type = 0

      if self.player == 2:

          if self.attacking == False and self.alive == True and round_over == False:
              # 计算玩家2与目标的水平和垂直距离
              dist_x = target.rect.centerx - self.rect.centerx
              dist_y = target.rect.centery - self.rect.centery

              # 控制水平移动
              if abs(dist_x) > ATTACK_RANGE:
                  if dist_x < 0:
                      dx = -SPEED
                      self.running = True
                  elif dist_x > 0:
                      dx = SPEED
                      self.running = True
              if target.rect.centerx > self.rect.centerx:
                self.flip = False
              else:
                self.flip = True

              if abs(dist_x) <= ATTACK_RANGE:
                  import random
                  attack_choice = random.choice([0,0,0,1,2])

                  if attack_choice == 0:
                    pass
                  if attack_choice == 1:
                    self.attack_type = 1
                    self.attack(target)
                    self.attack_cooldown = 8
                  if attack_choice == 2:
                    self.attack_type = 2
                    self.attack(target)
                    self.attack_cooldown = 8

                  self.attacking = False


              if self.attack_cooldown > 0:
                  self.attack_cooldown -= 1

          # 更新玩家2的位置
              self.rect.x += dx
              self.rect.y += dy





  #處理動畫更新
  def update(self):
    #檢查玩家正在執行什麼動作
    if self.health <= 0:
      self.health = 0
      self.alive = False
      self.update_action(6)#6:death
    elif self.hit == True:
      self.update_action(5)#5:hit
    elif self.attacking == True:
      if self.attack_type == 1:
        self.update_action(3)#3:attack1
      elif self.attack_type == 2:
        self.update_action(4)#4:attack2
    elif self.jump == True:
      self.update_action(2)#2:jump
    elif self.running == True:
      self.update_action(1)#1:run
    else:
      self.update_action(0)#0:idle

    animation_cooldown = 50
    #更新影像
    self.image = self.animation_list[self.action][self.frame_index]
    #檢查自上次更新以來是否已經過了足夠的時間
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    #檢查動畫是否完成
    if self.frame_index >= len(self.animation_list[self.action]):
      #如果玩家死亡則結束動畫
      if self.alive == False:
        self.frame_index = len(self.animation_list[self.action]) - 1
      else:
        self.frame_index = 0
        #檢查是否執行了攻擊
        if self.action == 3 or self.action == 4:
          self.attacking = False
          self.attack_cooldown = 20
        #檢查是否有損壞
        if self.action == 5:
          self.hit = False
          #如果玩家正在攻擊，那麼攻擊就會停止
          self.attacking = False
          self.attack_cooldown = 20

  def attack(self, target):
    if self.attack_cooldown == 0:
      #執行攻擊
      self.attacking = True
      self.attack_sound.play()
      attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
      if attacking_rect.colliderect(target.rect):
        target.health -= 10
        target.hit = True


  def update_action(self, new_action):
    #檢查新動作是否與前一個動作不同
    if new_action != self.action:
      self.action = new_action
      #更新動畫設定
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def draw(self, surface):
    img = pygame.transform.flip(self.image, self.flip, False)
    surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))