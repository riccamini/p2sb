import fastdeploy as fd
import numpy as np
import cv2
import os
import logging
import skimage.exposure

# Logger init
logging.basicConfig(
    level=os.getenv('LOG_LEVEL'),
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
logger = logging.getLogger(__name__)

class MattingService:

    def __init__(self, model_path, params_path, config_path, output_dir):
        # Setting runtime option for the deployment. We default to CPU

        logger.debug(f"Init mode with:\nModel path: {model_path}\nParams path: {params_path}\nConfig path: {config_path}")
        #option = fd.RuntimeOption()

        # Init model and vars
        #self.model = fd.vision.matting.PPMatting(model_path, params_path, config_path, runtime_option=option)
        self.model = fd.vision.matting.PPMatting(model_path, params_path, config_path)
        self.output_dir = output_dir
    
    def __remove_greenscreen(self, img):
        """
            Implementation from S.O.
            Reference: https://stackoverflow.com/questions/51719472/remove-green-background-screen-from-image-using-opencv-python?rq=1
        """
        # convert to LAB
        lab = cv2.cvtColor(img,cv2.COLOR_BGR2LAB)
        
        # extract A channel
        A = lab[:,:,1]
        
        # threshold A channel
        thresh = cv2.threshold(A, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        
        # blur threshold image
        blur = cv2.GaussianBlur(thresh, (0,0), sigmaX=5, sigmaY=5, borderType = cv2.BORDER_DEFAULT)
        
        # stretch so that 255 -> 255 and 127.5 -> 0
        mask = skimage.exposure.rescale_intensity(blur, in_range=(127.5,255), out_range=(0,255)).astype(np.uint8)
        
        # add mask to image as alpha channel
        result = img.copy()
        result = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
        result[:,:,3] = mask

        return result
    
    def matt_image(self, image_path):
        logger.info(f"Matting image {image_path}")
        input_image = cv2.imread(image_path)

        result = self.model.predict(input_image)
        logger.debug(f"Matting results: {result}")

        # Getting filename from input path
        original_filename = os.path.basename(image_path).split(".")[0]
        target_filepath = self.output_dir + "/" + original_filename + "_matted.png"

        logger.debug(f"Original filename: {original_filename}\nTarget filepath: {target_filepath}")

        # Get output image, add alpha channel and apply mask
        output_image = fd.vision.vis_matting(input_image, result)
        output_image_rgba = self.__remove_greenscreen(output_image)

        cv2.imwrite(target_filepath, output_image_rgba)

        return target_filepath
