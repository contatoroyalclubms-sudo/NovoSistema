"""
Ultra-Performance CDN Integration System
Sistema Universal de Gestão de Eventos - Static Asset Optimization
Target: Global asset delivery, sub-100ms static content, intelligent caching
"""

import asyncio
import logging
import hashlib
import mimetypes
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, BinaryIO
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import aiohttp
import aiofiles
import json
from urllib.parse import urlparse, urljoin
from PIL import Image
import io

from app.core.cache_ultra_performance import ultra_cache

logger = logging.getLogger(__name__)

# ================================
# CDN CONFIGURATION
# ================================

class CDNProvider(Enum):
    """Supported CDN providers"""
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    BUNNY_CDN = "bunny_cdn"
    LOCAL_NGINX = "local_nginx"  # For development/testing

@dataclass
class CDNConfig:
    """CDN configuration with ultra-performance settings"""
    provider: CDNProvider = CDNProvider.CLOUDFLARE
    base_url: str = "https://cdn.eventos.com"
    
    # Authentication
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    zone_id: Optional[str] = None
    
    # Performance settings
    cache_ttl_seconds: int = 86400  # 24 hours default
    edge_cache_ttl_seconds: int = 604800  # 7 days
    browser_cache_ttl_seconds: int = 3600  # 1 hour
    
    # Upload settings
    max_file_size_mb: int = 100
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
        '.pdf', '.mp4', '.mp3', '.zip', '.csv', '.xlsx',
        '.js', '.css', '.woff2', '.woff', '.ttf'
    ])
    
    # Image optimization
    auto_image_optimization: bool = True
    image_formats: List[str] = field(default_factory=lambda: ['webp', 'jpeg', 'png'])
    image_quality: int = 85
    
    # Local storage (fallback)
    local_storage_path: str = "static_assets"
    local_base_url: str = "/static"

@dataclass
class AssetMetadata:
    """Metadata for uploaded assets"""
    file_id: str
    original_filename: str
    content_type: str
    file_size_bytes: int
    file_hash: str
    cdn_url: str
    local_path: Optional[str] = None
    upload_timestamp: datetime = field(default_factory=datetime.now)
    cache_key: Optional[str] = None
    optimized_versions: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

# ================================
# CDN PROVIDERS IMPLEMENTATIONS
# ================================

class BaseCDNProvider:
    """Base class for CDN providers"""
    
    def __init__(self, config: CDNConfig):
        self.config = config
    
    async def upload_asset(self, file_data: bytes, filename: str, content_type: str) -> AssetMetadata:
        """Upload asset to CDN"""
        raise NotImplementedError
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete asset from CDN"""
        raise NotImplementedError
    
    async def get_asset_url(self, asset_id: str, optimization_params: Optional[Dict] = None) -> str:
        """Get optimized asset URL"""
        raise NotImplementedError
    
    async def purge_cache(self, urls: List[str]) -> bool:
        """Purge CDN cache for specific URLs"""
        raise NotImplementedError
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get CDN usage statistics"""
        raise NotImplementedError

class CloudflareCDNProvider(BaseCDNProvider):
    """Cloudflare CDN integration with R2 storage"""
    
    async def upload_asset(self, file_data: bytes, filename: str, content_type: str) -> AssetMetadata:
        """Upload to Cloudflare R2 with automatic optimization"""
        file_hash = hashlib.sha256(file_data).hexdigest()
        file_id = f"{int(time.time())}_{file_hash[:12]}"
        
        # Generate R2 key
        r2_key = f"assets/{datetime.now().strftime('%Y/%m')}/{file_id}_{filename}"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": content_type,
            "Cache-Control": f"public, max-age={self.config.cache_ttl_seconds}",
        }
        
        # Upload to R2
        async with aiohttp.ClientSession() as session:
            upload_url = f"https://api.cloudflare.com/client/v4/accounts/{self.config.zone_id}/r2/buckets/eventos-assets/objects/{r2_key}"
            
            async with session.put(upload_url, data=file_data, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Cloudflare upload failed: {response.status}")
        
        # Generate CDN URL with optimizations
        cdn_url = f"{self.config.base_url}/{r2_key}"
        if self.config.auto_image_optimization and content_type.startswith('image/'):
            cdn_url += "?format=auto&quality=85"
        
        return AssetMetadata(
            file_id=file_id,
            original_filename=filename,
            content_type=content_type,
            file_size_bytes=len(file_data),
            file_hash=file_hash,
            cdn_url=cdn_url,
            cache_key=r2_key
        )
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete from Cloudflare R2"""
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        
        async with aiohttp.ClientSession() as session:
            delete_url = f"https://api.cloudflare.com/client/v4/accounts/{self.config.zone_id}/r2/buckets/eventos-assets/objects/{asset_id}"
            
            async with session.delete(delete_url, headers=headers) as response:
                return response.status == 204
    
    async def get_asset_url(self, asset_id: str, optimization_params: Optional[Dict] = None) -> str:
        """Get optimized Cloudflare URL with transformations"""
        base_url = f"{self.config.base_url}/{asset_id}"
        
        if optimization_params:
            params = []
            
            # Image optimizations
            if optimization_params.get('width'):
                params.append(f"width={optimization_params['width']}")
            if optimization_params.get('height'):
                params.append(f"height={optimization_params['height']}")
            if optimization_params.get('quality'):
                params.append(f"quality={optimization_params['quality']}")
            if optimization_params.get('format'):
                params.append(f"format={optimization_params['format']}")
            
            # Performance optimizations
            if optimization_params.get('auto_optimize', True):
                params.append("format=auto")
            
            if params:
                base_url += "?" + "&".join(params)
        
        return base_url
    
    async def purge_cache(self, urls: List[str]) -> bool:
        """Purge Cloudflare cache"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {"files": urls}
        
        async with aiohttp.ClientSession() as session:
            purge_url = f"https://api.cloudflare.com/client/v4/zones/{self.config.zone_id}/purge_cache"
            
            async with session.post(purge_url, json=payload, headers=headers) as response:
                return response.status == 200

class LocalCDNProvider(BaseCDNProvider):
    """Local file storage with Nginx serving (development/fallback)"""
    
    def __init__(self, config: CDNConfig):
        super().__init__(config)
        self.storage_path = Path(config.local_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_asset(self, file_data: bytes, filename: str, content_type: str) -> AssetMetadata:
        """Save file locally"""
        file_hash = hashlib.sha256(file_data).hexdigest()
        file_id = f"{int(time.time())}_{file_hash[:12]}"
        
        # Create directory structure
        date_path = datetime.now().strftime('%Y/%m')
        file_dir = self.storage_path / date_path
        file_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = file_dir / f"{file_id}_{filename}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)
        
        # Generate URL
        cdn_url = f"{self.config.local_base_url}/{date_path}/{file_id}_{filename}"
        
        return AssetMetadata(
            file_id=file_id,
            original_filename=filename,
            content_type=content_type,
            file_size_bytes=len(file_data),
            file_hash=file_hash,
            cdn_url=cdn_url,
            local_path=str(file_path)
        )
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete local file"""
        # This would require storing file paths
        # For now, return True as placeholder
        return True
    
    async def get_asset_url(self, asset_id: str, optimization_params: Optional[Dict] = None) -> str:
        """Get local file URL"""
        return f"{self.config.local_base_url}/{asset_id}"
    
    async def purge_cache(self, urls: List[str]) -> bool:
        """No-op for local storage"""
        return True

# ================================
# ASSET OPTIMIZATION
# ================================

class ImageOptimizer:
    """High-performance image optimization"""
    
    @staticmethod
    async def optimize_image(
        image_data: bytes, 
        format: str = 'webp',
        quality: int = 85,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> bytes:
        """Optimize image with format conversion and resizing"""
        
        # Load image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            if format.lower() == 'jpeg':
                # Create white background for JPEG
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif format.lower() == 'webp':
                # WebP supports transparency
                image = image.convert('RGBA')
        
        # Resize if needed
        if max_width or max_height:
            original_width, original_height = image.size
            
            # Calculate new dimensions maintaining aspect ratio
            if max_width and max_height:
                ratio = min(max_width / original_width, max_height / original_height)
            elif max_width:
                ratio = max_width / original_width
            else:
                ratio = max_height / original_height
            
            if ratio < 1:  # Only downscale
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save optimized image
        output = io.BytesIO()
        
        save_kwargs = {
            'format': format.upper(),
            'optimize': True
        }
        
        if format.lower() in ['jpeg', 'webp']:
            save_kwargs['quality'] = quality
        
        if format.lower() == 'webp':
            save_kwargs['method'] = 6  # Best compression
        
        image.save(output, **save_kwargs)
        return output.getvalue()
    
    @staticmethod
    async def generate_responsive_images(
        image_data: bytes,
        sizes: List[int] = None
    ) -> Dict[str, bytes]:
        """Generate multiple sizes for responsive images"""
        if sizes is None:
            sizes = [480, 768, 1024, 1920]  # Mobile, tablet, desktop, large desktop
        
        responsive_images = {}
        
        for size in sizes:
            try:
                optimized = await ImageOptimizer.optimize_image(
                    image_data,
                    format='webp',
                    quality=85,
                    max_width=size
                )
                responsive_images[f"{size}w"] = optimized
            except Exception as e:
                logger.warning(f"Failed to generate {size}px version: {e}")
        
        return responsive_images

# ================================
# CDN MANAGER
# ================================

class UltraPerformanceCDN:
    """Ultra-performance CDN management system"""
    
    def __init__(self, config: CDNConfig = None):
        self.config = config or CDNConfig()
        self.provider = self._create_provider()
        self.asset_cache_ttl = 3600  # 1 hour cache for asset metadata
    
    def _create_provider(self) -> BaseCDNProvider:
        """Create CDN provider instance"""
        if self.config.provider == CDNProvider.CLOUDFLARE:
            return CloudflareCDNProvider(self.config)
        elif self.config.provider == CDNProvider.LOCAL_NGINX:
            return LocalCDNProvider(self.config)
        else:
            raise ValueError(f"Unsupported CDN provider: {self.config.provider}")
    
    async def upload_file(
        self,
        file_data: Union[bytes, BinaryIO],
        filename: str,
        content_type: Optional[str] = None,
        tags: List[str] = None,
        optimize_images: bool = True
    ) -> AssetMetadata:
        """Upload file with automatic optimization"""
        
        # Read file data if BinaryIO
        if hasattr(file_data, 'read'):
            file_bytes = await file_data.read() if hasattr(file_data, 'read') else file_data
        else:
            file_bytes = file_data
        
        # Detect content type
        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = 'application/octet-stream'
        
        # Validate file size
        file_size_mb = len(file_bytes) / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB > {self.config.max_file_size_mb}MB")
        
        # Validate file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.config.allowed_extensions:
            raise ValueError(f"File type not allowed: {file_ext}")
        
        # Optimize images if enabled
        optimized_versions = {}
        if optimize_images and content_type.startswith('image/'):
            try:
                # Generate WebP version
                webp_data = await ImageOptimizer.optimize_image(
                    file_bytes, 
                    format='webp',
                    quality=self.config.image_quality
                )
                
                # Upload WebP version
                webp_filename = Path(filename).stem + '.webp'
                webp_metadata = await self.provider.upload_asset(
                    webp_data, webp_filename, 'image/webp'
                )
                optimized_versions['webp'] = webp_metadata.cdn_url
                
                # Generate responsive sizes
                responsive_images = await ImageOptimizer.generate_responsive_images(file_bytes)
                
                for size_key, size_data in responsive_images.items():
                    size_filename = f"{Path(filename).stem}_{size_key}.webp"
                    size_metadata = await self.provider.upload_asset(
                        size_data, size_filename, 'image/webp'
                    )
                    optimized_versions[f"webp_{size_key}"] = size_metadata.cdn_url
                
            except Exception as e:
                logger.warning(f"Image optimization failed: {e}")
        
        # Upload original file
        metadata = await self.provider.upload_asset(file_bytes, filename, content_type)
        metadata.optimized_versions = optimized_versions
        metadata.tags = tags or []
        
        # Cache metadata
        cache_key = f"cdn_asset:{metadata.file_id}"
        await ultra_cache.set(cache_key, metadata.__dict__, ttl_seconds=self.asset_cache_ttl, namespace="cdn")
        
        logger.info(f"✅ Asset uploaded: {filename} ({len(optimized_versions)} optimized versions)")
        
        return metadata
    
    async def get_asset_metadata(self, asset_id: str) -> Optional[AssetMetadata]:
        """Get asset metadata from cache or storage"""
        cache_key = f"cdn_asset:{asset_id}"
        
        # Try cache first
        cached_data = await ultra_cache.get(cache_key, "cdn")
        if cached_data:
            return AssetMetadata(**cached_data)
        
        return None
    
    async def get_optimized_url(
        self,
        asset_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        format: Optional[str] = None,
        quality: Optional[int] = None,
        responsive_size: Optional[str] = None
    ) -> str:
        """Get optimized asset URL with caching"""
        
        # Create cache key for URL
        params = {
            'width': width,
            'height': height, 
            'format': format,
            'quality': quality,
            'responsive_size': responsive_size
        }
        param_str = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        url_cache_key = f"cdn_url:{asset_id}:{hashlib.md5(param_str.encode()).hexdigest()}"
        
        # Try cache first
        cached_url = await ultra_cache.get(url_cache_key, "cdn")
        if cached_url:
            return cached_url
        
        # Get asset metadata
        metadata = await self.get_asset_metadata(asset_id)
        if not metadata:
            raise ValueError(f"Asset not found: {asset_id}")
        
        # Check for pre-generated responsive versions
        if responsive_size and f"webp_{responsive_size}" in metadata.optimized_versions:
            url = metadata.optimized_versions[f"webp_{responsive_size}"]
        elif format == 'webp' and 'webp' in metadata.optimized_versions:
            url = metadata.optimized_versions['webp']
        else:
            # Use provider's dynamic optimization
            optimization_params = {k: v for k, v in params.items() if v is not None}
            url = await self.provider.get_asset_url(asset_id, optimization_params)
        
        # Cache URL for 1 hour
        await ultra_cache.set(url_cache_key, url, ttl_seconds=3600, namespace="cdn")
        
        return url
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete asset and clear caches"""
        # Delete from CDN
        success = await self.provider.delete_asset(asset_id)
        
        if success:
            # Clear caches
            await ultra_cache.delete(f"cdn_asset:{asset_id}", "cdn")
            
            # Clear URL caches (pattern-based)
            await ultra_cache.invalidate_pattern(f"cdn_url:{asset_id}:*", "cdn")
            
            logger.info(f"🗑️ Asset deleted: {asset_id}")
        
        return success
    
    async def purge_cache(self, asset_ids: List[str]) -> bool:
        """Purge CDN edge cache for assets"""
        # Get URLs to purge
        urls = []
        for asset_id in asset_ids:
            metadata = await self.get_asset_metadata(asset_id)
            if metadata:
                urls.append(metadata.cdn_url)
                urls.extend(metadata.optimized_versions.values())
        
        if urls:
            success = await self.provider.purge_cache(urls)
            logger.info(f"🧹 CDN cache purged for {len(urls)} URLs")
            return success
        
        return True
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive CDN usage statistics"""
        try:
            provider_stats = await self.provider.get_usage_stats()
            
            # Add cache statistics
            cache_stats = await ultra_cache.get_stats()
            
            return {
                "provider": self.config.provider.value,
                "provider_stats": provider_stats,
                "cache_stats": cache_stats.get("cdn", {}),
                "config": {
                    "auto_optimization": self.config.auto_image_optimization,
                    "max_file_size_mb": self.config.max_file_size_mb,
                    "allowed_extensions": len(self.config.allowed_extensions)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """CDN system health check"""
        try:
            # Test upload small file
            test_data = b"CDN health check test"
            test_metadata = await self.provider.upload_asset(
                test_data, "health_check.txt", "text/plain"
            )
            
            # Test URL generation
            test_url = await self.provider.get_asset_url(test_metadata.file_id)
            
            # Cleanup test file
            await self.provider.delete_asset(test_metadata.file_id)
            
            return {
                "status": "healthy",
                "provider": self.config.provider.value,
                "upload_test": "passed",
                "url_generation": "passed",
                "base_url": self.config.base_url
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.config.provider.value
            }

# ================================
# FASTAPI INTEGRATION
# ================================

from fastapi import UploadFile, HTTPException, Form
from fastapi.responses import RedirectResponse

# Global CDN instance
ultra_cdn = UltraPerformanceCDN()

async def init_ultra_cdn(config: CDNConfig = None):
    """Initialize ultra-performance CDN system"""
    global ultra_cdn
    if config:
        ultra_cdn = UltraPerformanceCDN(config)
    
    logger.info(f"✅ Ultra-Performance CDN initialized ({ultra_cdn.config.provider.value})")

# FastAPI route helpers
async def upload_file_endpoint(
    file: UploadFile,
    tags: str = Form(default=""),
    optimize: bool = Form(default=True)
):
    """FastAPI endpoint for file upload"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file data
        file_data = await file.read()
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Upload to CDN
        metadata = await ultra_cdn.upload_file(
            file_data=file_data,
            filename=file.filename,
            content_type=file.content_type,
            tags=tag_list,
            optimize_images=optimize
        )
        
        return {
            "success": True,
            "file_id": metadata.file_id,
            "cdn_url": metadata.cdn_url,
            "optimized_versions": metadata.optimized_versions,
            "file_size_bytes": metadata.file_size_bytes,
            "upload_timestamp": metadata.upload_timestamp.isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

# Export main components
__all__ = [
    'ultra_cdn', 'CDNConfig', 'CDNProvider', 'AssetMetadata',
    'init_ultra_cdn', 'upload_file_endpoint'
]