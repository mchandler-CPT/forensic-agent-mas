import os
import pickle
import cv2
import numpy as np

# Config
IMAGE_DIR = "reference_images/MOM"
INDEX_FILE = "card_features.pkl" 

def build_feature_index():
    print(f"🏗️  Building FULL CARD Feature Index from {IMAGE_DIR}...")
    
    if not os.path.exists(IMAGE_DIR):
        print("❌ Image directory not found.")
        return

    # Increase features to capture borders/text AND art
    orb = cv2.ORB_create(nfeatures=2000)
    
    index = {}
    files = os.listdir(IMAGE_DIR)
    
    print(f"   Processing {len(files)} images...")
    
    count = 0
    for filename in files:
        if not filename.endswith(".jpg"):
            continue
            
        uuid = filename.replace(".jpg", "")
        path = os.path.join(IMAGE_DIR, filename)
        
        try:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None: continue

            # --- CHANGE: NO CROP. USE THE WHOLE CARD. ---
            # We want the text box, the borders, the mana symbols.
            # These provide strong geometric anchors for rotation matching.
            
            keypoints, descriptors = orb.detectAndCompute(img, None)
            
            if descriptors is not None:
                index[uuid] = descriptors
                count += 1
                
            if count % 50 == 0:
                print(f"     -> Indexed {count}...")
                
        except Exception as e:
            print(f"     ❌ Failed {filename}: {e}")

    print(f"✅ Indexing complete. Saving {len(index)} feature sets to {INDEX_FILE}...")
    
    with open(INDEX_FILE, 'wb') as f:
        pickle.dump(index, f)

if __name__ == "__main__":
    build_feature_index()