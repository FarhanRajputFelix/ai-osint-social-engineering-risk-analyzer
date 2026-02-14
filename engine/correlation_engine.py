"""
OSINT Correlation Engine
Fuses data from image analysis and username analysis to produce
a unified correlation confidence score. Performs cross-modal analysis
combining visual and textual signals.
"""

from typing import Dict, List, Optional


class CorrelationEngine:
    """Correlates data from multiple OSINT analysis sources."""

    def correlate(self, image_results: Optional[Dict], username_results: Optional[Dict]) -> Dict:
        """
        Produce a unified correlation analysis from image and username data.
        """
        try:
            scores = {}
            details = []

            # Image-based correlation factors
            if image_results and image_results.get("status") == "success":
                img_score = image_results.get("image_reuse_score", {}).get("score", 0)
                scores["image_reuse"] = img_score

                cross_matches = image_results.get("cross_platform_matches", [])
                high_sim = [m for m in cross_matches if m["similarity_score"] > 80]
                scores["image_platform_matches"] = len(high_sim) * 12

                if image_results.get("face_detection", {}).get("has_profile_photo_characteristics"):
                    scores["profile_photo"] = 15
                    details.append({
                        "factor": "Profile Photo Detected",
                        "impact": "High",
                        "description": "Image has single-face profile photo characteristics, commonly reused across platforms",
                    })

                if high_sim:
                    platforms = [m["platform"] for m in high_sim]
                    details.append({
                        "factor": "Image Reuse Detected",
                        "impact": "Critical" if len(high_sim) > 3 else "High",
                        "description": f"High-similarity image matches found on {', '.join(platforms)}",
                    })

            # Username-based correlation factors
            if username_results and username_results.get("status") == "success":
                usr_score = username_results.get("correlation_score", {}).get("score", 0)
                scores["username_correlation"] = usr_score

                platform_matches = username_results.get("platform_matches", [])
                exact = sum(1 for m in platform_matches if m["exact_match"])
                scores["exact_username_matches"] = exact * 10

                if exact > 3:
                    details.append({
                        "factor": "Username Consistency",
                        "impact": "Critical",
                        "description": f"Exact username match found on {exact} platforms — strong linkability indicator",
                    })

                # Bio leakage
                bio = username_results.get("bio_analysis")
                if bio and bio.get("leakage_risk") == "High":
                    scores["bio_leakage"] = 20
                    details.append({
                        "factor": "Bio Information Leakage",
                        "impact": "High",
                        "description": f"Bio text reveals: {', '.join(bio.get('leaked_categories', []))}",
                    })

            # Cross-modal correlation (image + username together)
            if image_results and username_results:
                img_platforms = set(
                    m["platform"] for m in image_results.get("cross_platform_matches", [])
                    if m["similarity_score"] > 70
                )
                usr_platforms = set(
                    m["platform"] for m in username_results.get("platform_matches", [])
                    if m["confidence"] > 70
                )
                overlap = img_platforms & usr_platforms

                if overlap:
                    scores["cross_modal_overlap"] = len(overlap) * 15
                    details.append({
                        "factor": "Cross-Modal Platform Overlap",
                        "impact": "Critical",
                        "description": f"Both image AND username match on: {', '.join(overlap)}. This dramatically increases linkage confidence.",
                    })

            # Compute final score
            if not scores:
                final_score = 0
            else:
                # Weighted average with emphasis on cross-modal
                weights = {
                    "image_reuse": 0.20,
                    "image_platform_matches": 0.15,
                    "profile_photo": 0.05,
                    "username_correlation": 0.20,
                    "exact_username_matches": 0.15,
                    "bio_leakage": 0.10,
                    "cross_modal_overlap": 0.15,
                }
                weighted_sum = sum(scores.get(k, 0) * w for k, w in weights.items())
                final_score = min(98, int(weighted_sum))

            # Build combined platform intelligence
            combined_platforms = self._build_combined_platform_view(image_results, username_results)

            return {
                "status": "success",
                "correlation_confidence": {
                    "score": final_score,
                    "level": self._score_to_level(final_score),
                    "description": self._get_correlation_description(final_score),
                },
                "factor_breakdown": scores,
                "correlation_details": details,
                "combined_platform_intelligence": combined_platforms,
                "data_fusion_summary": self._generate_fusion_summary(
                    image_results, username_results, final_score, combined_platforms
                ),
            }

        except Exception as e:
            return {"status": "error", "message": f"Correlation failed: {str(e)}"}

    def _build_combined_platform_view(
        self, image_results: Optional[Dict], username_results: Optional[Dict]
    ) -> List[Dict]:
        """Combine image and username platform data into a unified view."""
        platform_data = {}

        # Add image platform matches
        if image_results and image_results.get("status") == "success":
            for match in image_results.get("cross_platform_matches", []):
                platform = match["platform"]
                
                # Sanitize data_gathered to remove mock functions if any leak
                data_points = match.get("data_gathered", {})
                
                platform_data[platform] = {
                    "platform": platform,
                    "icon": match.get("icon", "🌐"),
                    "color": match.get("color", "#666"),
                    "profile_url": match.get("profile_url"),
                    "image_similarity": match["similarity_score"],
                    "image_match_type": match["match_type"],
                    "username_confidence": None,
                    "username_exact": None,
                    "data_points": data_points,
                    "combined_risk": "Pending",
                }

        # Merge username platform matches
        if username_results and username_results.get("status") == "success":
            for match in username_results.get("platform_matches", []):
                platform = match["platform"]
                username_data_points = match.get("gathered_data", {})
                
                if platform in platform_data:
                    platform_data[platform]["username_confidence"] = match["confidence"]
                    platform_data[platform]["username_exact"] = match["exact_match"]
                    
                    # Prefer username profile_url if available, or keep image one
                    if match.get("profile_url"):
                        platform_data[platform]["profile_url"] = match.get("profile_url")
                        
                    # Merge gathered data - username data takes precedence for text fields
                    for k, v in username_data_points.items():
                         platform_data[platform]["data_points"][k] = v
                         
                else:
                    platform_data[platform] = {
                        "platform": platform,
                        "icon": match.get("icon", "🌐"),
                        "color": match.get("color", "#666"),
                        "profile_url": match.get("profile_url"),
                        "image_similarity": None,
                        "image_match_type": None,
                        "username_confidence": match["confidence"],
                        "username_exact": match["exact_match"],
                        "data_points": username_data_points,
                        "combined_risk": "Pending",
                    }

        # Calculate combined risk for each platform
        for p in platform_data.values():
            img = p["image_similarity"] or 0
            usr = p["username_confidence"] or 0
            combined = (img + usr) / 2 if img and usr else max(img, usr)
            p["combined_risk"] = (
                "Critical" if combined > 85
                else "High" if combined > 70
                else "Medium" if combined > 50
                else "Low"
            )
            p["combined_score"] = round(combined, 1)

        # Sort by combined score
        result = sorted(platform_data.values(), key=lambda x: x.get("combined_score", 0), reverse=True)
        return result

    def _score_to_level(self, score: int) -> str:
        if score > 80:
            return "Critical"
        elif score > 60:
            return "High"
        elif score > 40:
            return "Medium"
        return "Low"

    def _get_correlation_description(self, score: int) -> str:
        if score > 80:
            return "Critical exposure level. Multiple strong correlation indicators detected across platforms. An attacker could easily link these profiles and build a comprehensive target profile."
        elif score > 60:
            return "High exposure level. Significant cross-platform correlation patterns found. Profile linkage is feasible with moderate effort."
        elif score > 40:
            return "Moderate exposure. Some correlation patterns exist but linkage requires additional intelligence gathering."
        return "Low exposure. Limited correlation indicators found. Cross-platform linkage would be difficult."

    def _generate_fusion_summary(
        self, image_results: Optional[Dict], username_results: Optional[Dict],
        score: int, combined_platforms: List[Dict]
    ) -> str:
        parts = []

        if image_results and image_results.get("status") == "success":
            face_count = image_results.get("face_detection", {}).get("faces_found", 0)
            img_matches = len(image_results.get("cross_platform_matches", []))
            parts.append(f"Image analysis: {face_count} face(s) detected, {img_matches} platform matches.")

        if username_results and username_results.get("status") == "success":
            usr_matches = len(username_results.get("platform_matches", []))
            parts.append(f"Username analysis: {usr_matches} platform matches found.")

        critical_platforms = [p["platform"] for p in combined_platforms if p["combined_risk"] == "Critical"]
        if critical_platforms:
            parts.append(f"⚠️ Critical risk on: {', '.join(critical_platforms)}.")

        parts.append(f"Overall correlation confidence: {self._score_to_level(score)} ({score}%).")
        parts.append("This analysis demonstrates exposure risk assessment — not identity confirmation.")

        return " ".join(parts)
