"""
AI-Based Image Similarity Analysis Engine
Uses OpenCV for face detection, perceptual hashing for image similarity,
and color histogram analysis for visual fingerprinting.
CEH-Compliant: No facial recognition or identity guessing.
"""

import io
import hashlib
import numpy as np
from PIL import Image, ExifTags
import cv2
import imagehash
import random
from typing import Dict, List, Optional, Tuple


# Simulated platform image databases (for demo purposes)
SIMULATED_PLATFORMS = {
    "LinkedIn": {
        "icon": "💼", "color": "#0A66C2",
        "base_url": "https://linkedin.com/in/",
        "profile_fields": ["headline", "company", "location", "connections", "experience"],
    },
    "Twitter/X": {
        "icon": "🐦", "color": "#1DA1F2",
        "base_url": "https://twitter.com/",
        "profile_fields": ["bio", "followers", "following", "tweets", "location"],
    },
    "Facebook": {
        "icon": "📘", "color": "#1877F2",
        "base_url": "https://facebook.com/",
        "profile_fields": ["about", "friends", "photos", "workplace", "education"],
    },
    "Instagram": {
        "icon": "📷", "color": "#E4405F",
        "base_url": "https://instagram.com/",
        "profile_fields": ["bio", "followers", "following", "posts", "highlights"],
    },
    "GitHub": {
        "icon": "🐙", "color": "#333333",
        "base_url": "https://github.com/",
        "profile_fields": ["bio", "repositories", "contributions", "organizations", "location"],
    },
    "Reddit": {
        "icon": "🤖", "color": "#FF4500",
        "base_url": "https://reddit.com/user/",
        "profile_fields": ["karma", "posts", "comments", "communities", "account_age"],
    },
    "TikTok": {
        "icon": "🎵", "color": "#010101",
        "base_url": "https://tiktok.com/@",
        "profile_fields": ["bio", "followers", "following", "likes", "videos"],
    },
    "Discord": {
        "icon": "💬", "color": "#5865F2",
        "base_url": "https://discord.com/users/",
        "profile_fields": ["bio", "servers", "mutual_friends", "badges", "status"],
    },
}


def to_python(val):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(val, (np.bool_,)):
        return bool(val)
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, np.ndarray):
        return val.tolist()
    return val


class ImageAnalyzer:
    """Analyzes images for face detection, feature extraction, and cross-platform similarity."""

    def __init__(self):
        # Load OpenCV's pre-trained Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )

    def analyze(self, image_bytes: bytes) -> Dict:
        """Main analysis pipeline for an uploaded image."""
        try:
            # Load image
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

            # Run analysis modules
            face_data = self._detect_faces(cv_image)
            perceptual_hash = self._compute_perceptual_hash(pil_image)
            color_profile = self._analyze_color_histogram(cv_image)
            image_metadata = self._extract_metadata(pil_image, image_bytes)
            
            # [MODIFIED] Real EXIF Data Extraction
            exif_data = self._extract_exif_data(pil_image)
            image_metadata.update(exif_data)

            # [MODIFIED] Conditional Persona Generation
            # Only generate a persona if we detected a face or it looks like a profile photo
            target_persona = None
            if face_data["faces_found"] > 0:
                 target_persona = self._generate_consistent_persona(perceptual_hash["composite_fingerprint"])
            else:
                 target_persona = {
                     "display_name": "Unknown Subject",
                     "job": "Unknown",
                     "location": "Unknown",
                     "bio_template": "No distinct persona detected in this image."
                 }
            
            cross_platform = self._simulate_cross_platform_search(perceptual_hash, face_data, target_persona)

            # Compute image reuse score
            reuse_score = self._compute_reuse_score(face_data, perceptual_hash, color_profile)

            return {
                "status": "success",
                "face_detection": face_data,
                "perceptual_hash": perceptual_hash,
                "color_profile": color_profile,
                "image_metadata": image_metadata,
                "cross_platform_matches": cross_platform,
                "image_reuse_score": reuse_score,
                "analysis_summary": self._generate_summary(face_data, reuse_score, cross_platform),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Image analysis failed: {str(e)}",
            }

    def _generate_consistent_persona(self, seed: str) -> Dict:
        """Generate a consistent persona based on image hash seed."""
        rng = random.Random(hash(seed))
        
        names = [
            "Alex Johnson", "Sarah Mitchell", "David Kim", "Jordan Taylor", 
            "Chris Morgan", "Riley Anderson", "Casey Parker", "Jamie Brooks", 
            "Morgan Lee", "Sam Rivera", "Taylor Nguyen", "Priya Patel"
        ]
        display_name = rng.choice(names)
        
        jobs = [
            "Photographer", "Graphic Designer", "Influencer", "Artist", 
            "Model", "Journalist", "Content Creator", "Entrepreneur"
        ]
        job = rng.choice(jobs)

        locations = [
            "San Francisco, CA", "New York, NY", "London, UK", "Austin, TX", 
            "Berlin, Germany", "Los Angeles, CA", "Paris, France", "Tokyo, Japan"
        ]
        location = rng.choice(locations)

        return {
            "display_name": display_name,
            "job": job,
            "location": location,
            "bio_template": f"{job} | Based in {location} | Creating visual stories."
        }

    def _detect_faces(self, cv_image: np.ndarray) -> Dict:
        """Detect faces using Haar Cascades. No identity recognition."""
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        face_details = []
        for i, (x, y, w, h) in enumerate(faces):
            roi_gray = gray[y : y + h, x : x + w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)

            face_details.append({
                "face_id": i + 1,
                "position": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "relative_size": round(float(w * h) / float(cv_image.shape[0] * cv_image.shape[1]) * 100, 2),
                "eyes_detected": int(len(eyes)),
                "confidence": round(min(95, 70 + len(eyes) * 10 + (w * h / 10000)), 1),
            })

        has_profile = bool(
            len(faces) == 1
            and len(face_details) > 0
            and face_details[0]["relative_size"] > 5
        )

        return {
            "faces_found": int(len(faces)),
            "details": face_details,
            "has_profile_photo_characteristics": has_profile,
        }

    def _compute_perceptual_hash(self, pil_image: Image.Image) -> Dict:
        """Compute multiple perceptual hashes for robust image fingerprinting."""
        ahash = str(imagehash.average_hash(pil_image))
        phash = str(imagehash.phash(pil_image))
        dhash = str(imagehash.dhash(pil_image))
        whash = str(imagehash.whash(pil_image))

        return {
            "average_hash": ahash,
            "perceptual_hash": phash,
            "difference_hash": dhash,
            "wavelet_hash": whash,
            "composite_fingerprint": hashlib.sha256(
                f"{ahash}{phash}{dhash}{whash}".encode()
            ).hexdigest()[:16],
        }

    def _analyze_color_histogram(self, cv_image: np.ndarray) -> Dict:
        """Analyze color distribution for visual fingerprinting."""
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Calculate histograms for each channel
        h_hist = cv2.calcHist([hsv], [0], None, [12], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [8], [0, 256])
        v_hist = cv2.calcHist([hsv], [2], None, [8], [0, 256])

        # Normalize
        h_hist = (h_hist / h_hist.sum() * 100).flatten().tolist()
        s_hist = (s_hist / s_hist.sum() * 100).flatten().tolist()
        v_hist = (v_hist / v_hist.sum() * 100).flatten().tolist()

        # Determine dominant color
        dominant_hue_idx = int(np.argmax(h_hist))
        hue_names = [
            "Red", "Orange", "Yellow", "Yellow-Green", "Green", "Cyan",
            "Light Blue", "Blue", "Purple", "Magenta", "Pink", "Red"
        ]

        avg_brightness = float(np.mean(hsv[:, :, 2]))
        avg_saturation = float(np.mean(hsv[:, :, 1]))

        profile_type = "Professional headshot"
        if avg_brightness > 120:
            profile_type = "Casual/outdoor photo"
        elif avg_brightness <= 100 or avg_saturation >= 100:
            profile_type = "Dark/artistic photo"
        elif avg_brightness > 100 and avg_saturation < 100:
            profile_type = "Professional headshot"

        return {
            "dominant_color": hue_names[dominant_hue_idx],
            "brightness": round(avg_brightness, 1),
            "saturation": round(avg_saturation, 1),
            "color_complexity": round(float(np.std(h_hist)), 2),
            "hue_distribution": [round(v, 1) for v in h_hist],
            "profile_type": profile_type,
        }

    def _extract_exif_data(self, pil_image: Image.Image) -> Dict:
        """Extract real EXIF metadata from the image."""
        exif_info = {}
        try:
            raw_exif = pil_image._getexif()
            if raw_exif:
                for tag, value in raw_exif.items():
                    decoded = ExifTags.TAGS.get(tag, tag)
                    if decoded in ["Make", "Model", "DateTimeOriginal", "Software", "LensModel"]:
                         exif_info[decoded] = str(value).strip()
                    # GPS handling is complex, simplified existence check for now
                    if decoded == "GPSInfo":
                        # [MODIFIED] User requested full metadata. 
                        # In a real tool, we would parse the nested GPS tags (lat/long refs).
                        # For now, we will indicate presence clearly.
                        exif_info["GPS_Data"] = "Present (Lat/Long Data Available)"
        except Exception:
            pass
        
        return {
            "camera_make": exif_info.get("Make", "Unknown"),
            "camera_model": exif_info.get("Model", "Unknown"),
            "capture_date": exif_info.get("DateTimeOriginal", "Unknown"),
            "software": exif_info.get("Software", "Unknown"),
            "gps_status": exif_info.get("GPS_Data", "Not Found"),
        }

    def _extract_metadata(self, pil_image: Image.Image, raw_bytes: bytes) -> Dict:
        """Extract non-sensitive image metadata."""
        is_square = bool(abs(pil_image.width - pil_image.height) < 20)
        return {
            "dimensions": {"width": pil_image.width, "height": pil_image.height},
            "format": pil_image.format or "Unknown",
            "mode": pil_image.mode,
            "file_size_kb": round(len(raw_bytes) / 1024, 1),
            "aspect_ratio": round(pil_image.width / max(pil_image.height, 1), 2),
            "is_square": is_square,
            "osint_note": "Square images are commonly used as profile photos across platforms",
        }

    def _simulate_cross_platform_search(self, hash_data: Dict, face_data: Dict, persona: Dict) -> List[Dict]:
        """Simulate cross-platform image reuse detection (demo/educational)."""
        rng = random.Random(hash(hash_data["composite_fingerprint"]))

        matches = []
        num_matches = rng.randint(2, 6)
        platforms = rng.sample(list(SIMULATED_PLATFORMS.keys()), min(num_matches, len(SIMULATED_PLATFORMS)))

        for platform in platforms:
            similarity = round(rng.uniform(60, 98), 1)
            info = SIMULATED_PLATFORMS[platform]

            # Generate a username consistent with persona name
            base_username = persona["display_name"].lower().replace(" ", "")
            sim_username = f"{base_username}{rng.randint(1,999)}"
            profile_url = f"{info['base_url']}{sim_username}"

            # Simulate gathered profile data
            has_bio = rng.choice([True, True, False])
            has_image = rng.choice([True, True, True, False])
            has_location = rng.choice([True, False, False])
            has_posts = rng.choice([True, True, False])
            has_connections = rng.choice([True, True, False])
            is_verified = rng.choice([False, False, False, True])

            connections_count = None
            if has_connections:
                connections_count = f"{rng.randint(50, 5000)}+"

            matches.append({
                "platform": platform,
                "icon": info["icon"],
                "color": info["color"],
                "similarity_score": similarity,
                "match_type": "Exact match" if similarity > 90 else "High similarity" if similarity > 75 else "Partial match",
                "image_variants_found": rng.randint(1, 4),
                "profile_type": rng.choice(["Personal", "Professional", "Public Page"]),
                "profile_url": profile_url, # Ensure URL is included
                "last_seen": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
                "data_gathered": {
                    "display_name": persona["display_name"],
                    "bio_available": has_bio,
                    "bio_text": persona["bio_template"] if has_bio else None,
                    "profile_image_available": has_image,
                    "location_visible": has_location,
                    "location": persona["location"] if has_location else None,
                    "connections_visible": has_connections,
                    "connections_count": connections_count,
                    "posts_public": has_posts,
                    "post_count": rng.randint(10, 500) if has_posts else 0,
                    "joined_date": f"20{rng.randint(16, 24)}-{rng.randint(1,12):02d}",
                    "verification_status": is_verified,
                    "account_active": rng.choice([True, True, True, False]),
                },
            })

        matches.sort(key=lambda m: m["similarity_score"], reverse=True)
        return matches

    def _compute_reuse_score(self, face_data: Dict, hash_data: Dict, color_profile: Dict) -> Dict:
        """Compute how likely this image is reused across platforms."""
        score = 30  # Base score

        if face_data["has_profile_photo_characteristics"]:
            score += 25
        if face_data["faces_found"] == 1:
            score += 15
        if color_profile["profile_type"] == "Professional headshot":
            score += 15
        if color_profile["brightness"] > 80:
            score += 5

        # Cap at 95
        score = min(95, score)

        return {
            "score": score,
            "level": "Critical" if score > 80 else "High" if score > 60 else "Medium" if score > 40 else "Low",
            "description": self._get_reuse_description(score),
        }

    def _get_reuse_description(self, score: int) -> str:
        if score > 80:
            return "This image has strong characteristics of a reused profile photo. High probability of cross-platform linkage."
        elif score > 60:
            return "This image shows significant indicators of being a profile photo that may be reused across platforms."
        elif score > 40:
            return "This image has moderate profile photo characteristics. Some cross-platform linkage possible."
        else:
            return "This image has low profile photo characteristics. Limited cross-platform exposure risk."

    def _generate_summary(self, face_data: Dict, reuse_score: Dict, cross_platform: List[Dict]) -> str:
        """Generate a CEH-safe analysis summary."""
        parts = []
        parts.append(f"Image analysis detected {face_data['faces_found']} face(s).")

        if face_data["has_profile_photo_characteristics"]:
            parts.append("The image exhibits profile photo characteristics (single face, centered composition).")

        parts.append(f"Image reuse risk: {reuse_score['level']} ({reuse_score['score']}%).")

        high_matches = [m for m in cross_platform if m["similarity_score"] > 80]
        if high_matches:
            platforms = ", ".join(m["platform"] for m in high_matches)
            parts.append(f"High-similarity matches detected on: {platforms}.")

        parts.append("WARNING: This analysis indicates exposure risk, not confirmed identity.")
        return " ".join(parts)
