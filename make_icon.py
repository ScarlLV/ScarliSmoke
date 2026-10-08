from PIL import Image
import pygame, os

# Генерируем картинку нашей иконки через pygame, сохраняем PNG,
# потом конвертим в .ico
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
surf = pygame.Surface((256, 256), pygame.SRCALPHA)
# ... (скопируй код make_window_icon сюда, но с size=256)
# упрощённо:
c = 128; r = 124
pygame.draw.circle(surf, (200, 25, 25), (c, c), r)
pygame.draw.circle(surf, (255, 255, 255), (c, c), r - 12)
cw, ch = 170, 40
cg = pygame.Surface((cw, ch), pygame.SRCALPHA)
pygame.draw.rect(cg, (245, 245, 240), (0, 0, 120, ch))
pygame.draw.rect(cg, (220, 170, 90), (120, 0, 50, ch))
surf.blit(cg, (c - cw // 2, c - ch // 2))
lw = 20
pygame.draw.line(surf, (200, 20, 20), (c-90, c-90), (c+90, c+90), lw)
pygame.draw.line(surf, (200, 20, 20), (c-90, c+90), (c+90, c-90), lw)

pygame.image.save(surf, "icon.png")
img = Image.open("icon.png")
img.save("icon.ico", sizes=[(16,16), (32,32), (48,48), (64,64),
                            (128,128), (256,256)])
print("icon.ico готов!")