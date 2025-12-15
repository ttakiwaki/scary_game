import random
import arcade
import math


# --- Constants ---
MOVE_SPEED = 10

SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_display_size()

class Monster(arcade.Sprite):
    def __init__(self, monster_sprite, scale, center_x, center_y, change_x, change_y):
        """ Constructor. """
        super().__init__(monster_sprite, scale)
        
        self.center_x = center_x
        self.center_y = center_y
        
        self.change_x = change_x
        self.change_y = change_y

        #stationary = False
        
    def look_for_point(self):
        x = random.randrange(SCREEN_WIDTH)
        y = random.randrange(SCREEN_HEIGHT)
        return x, y
    
    def update(self):
        """ Code to control the ball's movement"""
        # Move the ball
        self.center_y += self.change_y / 5
        self.center_x += self.change_x / 5
        
        #See if the ball hi the edge of the screen, If so change direction
        if self.center_x > SCREEN_WIDTH:
            self.change_x *= -1
            
        elif self.center_x < self.scale:
            self.change_x *= -1            
            
        elif self.center_y > SCREEN_HEIGHT:
            self.change_y *= -1    
    
        elif self.center_y < self.scale:
            self.change_y *= -1

        """Minecraft mob type movement. Find random [x,y] value, and once at the position, generate a new point to move to."""
        


    def calc_radius(self, coor):
        monster_distance = math.sqrt((coor[0] - self.center_x)**2 + (coor[1] - self.center_y)**2)
        global enable_tracking
        #print(monster_distance)
        if monster_distance  <= 400:
            enable_tracking = True
        else:
            enable_tracking = False
        
class Generator(arcade.Sprite):
    def __init__(self, generator_sprite_on, generator_sprite_off, scale, center_x, center_y):
        """Constructor"""
        super().__init__(generator_sprite_on, scale)
        
        #Location 
        self.center_x = center_x
        self.center_y = center_y
        self.gen_coor = [center_x, center_y]

        #Interactability States
        self.interactable = False
        self.generator_complete = False
        self.reach = 50

    def calc_interact(self, coor):
        generator_distance = math.dist(coor, self.gen_coor)
        if generator_distance  <= self.reach:
            self.interactable = True
        else:
            self.interactable = False

class MyGame(arcade.Window):
    """Our custom Window Class"""
       
    def __init__(self):
        """Initializer"""
        
        #Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Scary Game", fullscreen=False, resizable=True, update_rate=1/60)
        
        # Create the cameras. One for the GUI, one for the sprites.
        # We scroll the 'sprite world' but not the GUI.
        self.camera_for_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_for_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)        
        
        self.set_location(100,100)
        
        # Variables that will hold sprite lists.
        self.player_list = None
        self.monster_list = None
        self.tree_list = None
        self.generator_list = None
        
        #Set up the player info
        self.player_sprite = None
        
        #Set up environment info
        self.level = 1
        
        #True / False
        self.inventory_open = False
        self.enable_tracking = False
        self.gun_on = False
        self.left_pressed = False
        self.right_pressed = False
        
        #Integers
        self.score = 0
        self.angle = 0
        self.tree_count = 10
        self.generator_count = 3
        self.sanity_initial = 100

        #Audio
        self.bgm = arcade.load_sound("data/audio/bgm/06.There_In_Spirit.wav")

        #BGM Player
        self.bgm_player = arcade.play_sound(self.bgm, volume=0.1, looping=True)
        arcade.set_background_color(arcade.color.AMAZON)


    def close(self):
        """Close the Window and stop background music"""
        super().close()

    def setup(self):
        """Set up the game and initialize the variables."""
        
        def coordinate_generate():
            x = random.randrange(SCREEN_WIDTH)
            y = random.randrange(SCREEN_HEIGHT)            
            generated_coordinate = [x, y]
            return generated_coordinate
            
        #Sprite Lists
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.AnimatedTimeBasedSprite()
        texture = arcade.load_texture("data/sprites/sprite.png", x=0, y=0, width=32, height=32)
        anim = arcade.AnimationKeyframe(1,10,texture)
        self.player_sprite.frames.append(anim)
        
        #Set up the player
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 64
        self.player_list.append(self.player_sprite)
        self.inventory_dict = {
            "health_1": 0,
            "sanity_1": 0,
            "speed_1": 0,
            "health_2": 0,
            "sanity_2": 0,
            "speed_2": 0,}            
        
        #Set up the monster
        self.monster_list = arcade.SpriteList()
        monster = Monster("data/sprites/angry_face.png", 0.5, 10, 10, 10, 10)
        self.monster_list.append(monster)
        
        #Set up trees
        self.tree_list = arcade.SpriteList()
        for i in range(self.tree_count):
            tree_coor = coordinate_generate()
            tree = arcade.Sprite("data/sprites/tree_sprite.png", scale= 1, center_x= tree_coor[0], center_y= tree_coor[1])
            self.tree_list.append(tree)

        #Set up generators
        self.generator_list = arcade.SpriteList()
        for i in range(self.generator_count):
            generator_coor = coordinate_generate()

            generator = Generator("data/sprites/generator_sprite.png", "data/sprites/generator_sprite_on.png", scale= 0.2, center_x= generator_coor[0], center_y= generator_coor[1])
            self.generator_list.append(generator)

    def sanity_decrease(self):
        decrease_factor = 1.3
        rate_of_consumption = 1 * decrease_factor**(self.level-1)
        return rate_of_consumption

    def on_uidraw(self):
        #Draw gun
        x = 50 * math.sin(self.angle) + player_pos[0]
        y = 50 * math.cos(self.angle) + player_pos[1]
        if self.gun_on == True:
            arcade.draw_line(player_pos[0], player_pos[1], x, y, arcade.color.RED)
                                        
        #Draw Inventory
        if self.inventory_open == True:
            arcade.draw_rectangle_filled(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.BLACK)
            arcade.draw_text("Inventory:", SCREEN_WIDTH/4, SCREEN_HEIGHT/1.5, arcade.color.WHITE, 24)
            
            arcade.draw_text(f"Health Restore: T1: {self.inventory_dict['health_1']}, T2: {self.inventory_dict['health_2']}", SCREEN_WIDTH/4, SCREEN_HEIGHT/2, arcade.color.WHITE, 24)
            arcade.draw_text(f"Sanity Restore: T1: {self.inventory_dict['sanity_1']}, T2: {self.inventory_dict['sanity_2']}", SCREEN_WIDTH/4, SCREEN_HEIGHT/2.5, arcade.color.WHITE, 24)
            arcade.draw_text(f"Speed Restore: T1: {self.inventory_dict['speed_1']}, T2: {self.inventory_dict['speed_2']}", SCREEN_WIDTH/4, SCREEN_HEIGHT/3, arcade.color.WHITE, 24)
            
            arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.WHITE, 24)
            arcade.draw_text(f"In Radius: {enable_tracking}", 10, 50, arcade.color.WHITE, 24)
            arcade.draw_text(f"Sanity: {self.sanity_initial}", 10, 90, arcade.color.WHITE, 24)

        #Draw Sanity Bar bounds 
        rect_w = SCREEN_WIDTH / 4
        rect_h = SCREEN_HEIGHT / 12
        margin_x = 5  # pixels from right edge
        margin_y = 5  # pixels from bottom edge
        center_x = SCREEN_WIDTH - rect_w / 2 - margin_x
        center_y = rect_h / 2 + margin_y
        arcade.draw_rectangle_filled(center_x, center_y, rect_w, rect_h, arcade.color.BLACK)

        #Draw Sanity Bar
        # rect_w = SCREEN_WIDTH / 4
        # rect_h = SCREEN_HEIGHT / 10
        # margin_x = 10  # pixels from right edge
        # margin_y = 10  # pixels from bottom edge
        # center_x = SCREEN_WIDTH - rect_w / 2 - margin_x
        # center_y = rect_h / 2 + margin_y
        # arcade.draw_rectangle_filled(center_x, center_y, rect_w, rect_h, (136, 8, 8))


               
    def on_draw(self):
        arcade.start_render()
        
        #Draw Monster
        self.monster_list.draw()
        
        #Draw Sprites
        self.player_list.draw()
        
        #Draw Environment
        self.tree_list.draw()
        self.generator_list.draw()

        #Draw UI
        self.on_uidraw()

    def update(self, delta_time):
        """Movement and game logic"""
        
        #Call update on all sprites (Sprites dont do much in this example)
        self.player_list.update()
        self.player_list.update_animation()
        global player_pos
        player_pos = self.player_sprite.position

        #Sanity Decrease
        self.sanity_decrease()
        
        #Player Movement Update
        if SCREEN_WIDTH-10 < player_pos[0]:
            self.player_sprite.change_x = 0
            
        elif 20 > player_pos[0]:
            self.player_sprite.change_x = 0
                
        if SCREEN_HEIGHT-10 < player_pos[1]:
            self.player_sprite.change_y = 0
                
        elif 20 > player_pos[1]:
            self.player_sprite.change_y = 0
            
        #gun Update
        if self.left_pressed:
            self.angle -= 0.1
        elif self.right_pressed:
            self.angle += 0.1        

        #Monster Update
        for monster in self.monster_list:
            monster.calc_radius(player_pos)        

        self.monster_list.update()
        monster_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.monster_list)
        for monster_hit in monster_hit_list:
            self.score+=1

        #Generator Update
        for generator in self.generator_list:
            generator.calc_interact(player_pos)
            

    def commands(self):
        command = input(": ")
        if command == "give_health1":
            self.inventory_dict["health_1"] += 1
        elif command == "give_health2":
            self.inventory_dict["health_2"] += 1
        elif command == "give_sanity1":
            self.inventory_dict["sanity_1"] += 1
        elif command == "give_sanity2":
            self.inventory_dict["sanity_2"] += 1
        elif command == "give_speed1":
            self.inventory_dict["speed_1"] += 1
        elif command == "give_speed2":
            self.inventory_dict["speed_2"] += 1          
        
    def on_key_press(self, key, modifiers):
        """Check to see which key is being pressed and move the player in the
        appropriate direction"""
        
        #gun Angle
        if key == arcade.key.LEFT:
            self.left_pressed = True
        
        elif key == arcade.key.RIGHT:
            self.right_pressed += True    
        
        #Movement Keys (W, A, S, D)
        elif key == arcade.key.W:
            self.player_sprite.change_y = MOVE_SPEED
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = i * 32, y = 32, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,250,texture)
                self.player_sprite.frames.append(anim)
                
        elif key == arcade.key.S:
            self.player_sprite.change_y = -MOVE_SPEED
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = i * 32, y = 0, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,250,texture)
                self.player_sprite.frames.append(anim)
                
        elif key == arcade.key.D:
            self.player_sprite.change_x = MOVE_SPEED
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = i * 32, y = 96, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,250,texture)
                self.player_sprite.frames.append(anim)
                
        elif key == arcade.key.A:
            self.player_sprite.change_x = -MOVE_SPEED
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = i * 32, y = 64, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,250,texture)
                self.player_sprite.frames.append(anim)
        
        #Generator Interactivity Key
        elif key == arcade.key.E:
            for gen in self.generator_list:
                if gen.interactable == True and gen.generator_complete == False:
                    gen.generator_complete = True
                    gen.texture = arcade.load_texture("data/sprites/generator_sprite_on.png")

        #Inventory & gun Toggle
        elif key == arcade.key.K:
            if self.inventory_open == False:
                self.inventory_open = True
                print("Inventory Open")
            else:
                self.inventory_open = False
                print("Inventory Close")
                
        elif key == arcade.key.L:
            if self.gun_on == False:
                self.gun_on = True
                print("gun On")
            else:
                self.gun_on = False
                print("gun Off")        
        
        #Command Prompt
        elif key == arcade.key.T:
            self.commands()
             
    def on_key_release(self, key, modifiers):
        """Check to see which key is being pressed and move the player in the
        appropriate direction"""
        
        #gun Angle
        if key == arcade.key.LEFT:
            self.left_pressed = False
        
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        
        if key == arcade.key.W:
            self.player_sprite.change_y = 0
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = 0, y = 0, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,10,texture)
                self.player_sprite.frames.append(anim)            
                        
        elif key == arcade.key.S:
            self.player_sprite.change_y = 0
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = 0, y = 0, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,10,texture)
                self.player_sprite.frames.append(anim)            
                        
        elif key == arcade.key.D:
            self.player_sprite.change_x = 0
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = 0, y = 96, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,10,texture)
                self.player_sprite.frames.append(anim)
                
        elif key == arcade.key.A:
            self.player_sprite.change_x = 0
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = 0, y = 64, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,10,texture)
                self.player_sprite.frames.append(anim)            
            

def main():
    """Main Method"""
    window = MyGame()
    window.setup()
    arcade.run()
    
if __name__ == "__main__":
    main()