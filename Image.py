import win32gui
class Image(object):
    '''
    describe an Image to draw on doll window
    '''
    def __init__(self):
        self.components = []
        
    def append_component(self, bmp_handle, x, y, w, h):
        '''
        bmp_handle: path of bitmap
        w: width to draw
        h: height to draw
        '''
        self.components.append((bmp_handle, x, y, w, h))
    
    def draw_on_dc(self, dst_dc, mask_color):
        '''
        draw all components on dst_dc in the order of invoking append_componet
        mask_color: 0xaabbcc , the color will be transparent instead
        '''
        mdc = win32gui.CreateCompatibleDC(dst_dc)
        for bmp, x, y, w, h in self.components:
            win32gui.SelectObject(mdc,bmp)
            pybmp = win32gui.GetObject(bmp)
            src_w = pybmp.bmWidth
            src_h = pybmp.bmHeight
            win32gui.TransparentBlt(dst_dc, x, y, w, h, mdc, 0, 0, src_w, src_h, mask_color)
        win32gui.DeleteDC(mdc)
    def release_img(self):
        for bmp, x,y,w,h in self.components:
            win32gui.DeleteObject(bmp)
        self.components = None