#!/usr/bin/env python3
"""
qu2cu Service - Font Tools Quadratic to Cubic Conversion Service
Port: 8011
Purpose: Convert quadratic bezier curves to cubic bezier curves in font files
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import traceback

# Add fontTools to path
fonttools_path = "/Users/dansidanutz/Desktop/ZmartBot/zmart-api/venv/lib/python3.9/site-packages"
if fonttools_path not in sys.path:
    sys.path.insert(0, fonttools_path)

try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.qu2cuPen import Qu2CuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.misc.cliTools import makeOutputFileName
except ImportError as e:
    print(f"Error importing fontTools: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Service configuration
SERVICE_PORT = 8020
SERVICE_NAME = "qu2cu"
ALLOWED_EXTENSIONS = {'ttf', 'otf', 'woff', 'woff2'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_font_to_cubic(input_path, output_path=None, dump_stats=False):
    """Convert font file from quadratic to cubic bezier curves"""
    try:
        font = TTFont(input_path)
        logger.info(f"Converting curves for {input_path}")

        stats = {} if dump_stats else None
        qu2cu_kwargs = {
            "stats": stats,
            "dump_stats": dump_stats,
            "max_err": 0.1,  # Maximum error tolerance
            "reverse_direction": False,
            "remember_curvetype": True,
            "all_cubic": True
        }

        # Process each glyph
        for glyph_name in font.getGlyphOrder():
            glyph = font['glyf'][glyph_name]
            if hasattr(glyph, 'getComponents'):
                # Skip composite glyphs
                continue
            
            if hasattr(glyph, 'getCoordinates'):
                # Convert coordinates
                coords = glyph.getCoordinates(font['glyf'])[0]
                end_pts = glyph.getCoordinates(font['glyf'])[1]
                
                # Create pens for conversion
                qu2cu_pen = Qu2CuPen(TTGlyphPen(), **qu2cu_kwargs)
                
                # Draw the glyph
                glyph.draw(qu2cu_pen, font['glyf'])
                
                # Get the converted glyph
                converted_glyph = qu2cu_pen.glyph()
                
                # Replace the original glyph
                font['glyf'][glyph_name] = converted_glyph

        # Save the converted font
        if output_path is None:
            output_path = makeOutputFileName(input_path, outputDir=None, overWrite=True)
        
        font.save(output_path)
        logger.info(f"Conversion completed: {output_path}")
        
        return {
            "success": True,
            "input_path": input_path,
            "output_path": output_path,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error converting font: {e}")
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "service": SERVICE_NAME,
        "status": "healthy",
        "port": SERVICE_PORT,
        "version": "1.0.0"
    })

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check endpoint"""
    try:
        # Test fontTools import
        from fontTools.ttLib import TTFont
        return jsonify({
            "service": SERVICE_NAME,
            "status": "ready",
            "fontTools": "available"
        })
    except Exception as e:
        return jsonify({
            "service": SERVICE_NAME,
            "status": "not_ready",
            "error": str(e)
        }), 500

@app.route('/convert', methods=['POST'])
def convert_font():
    """Convert uploaded font file from quadratic to cubic"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            input_filename = secure_filename(file.filename)
            input_path = os.path.join(temp_dir, input_filename)
            file.save(input_path)
            
            # Generate output filename
            output_filename = f"converted_{input_filename}"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Convert the font
            result = convert_font_to_cubic(input_path, output_path)
            
            if result["success"]:
                # Return the converted file
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=output_filename,
                    mimetype='application/octet-stream'
                )
            else:
                return jsonify(result), 500
                
    except Exception as e:
        logger.error(f"Error in convert endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/info', methods=['GET'])
def service_info():
    """Get service information"""
    return jsonify({
        "service": SERVICE_NAME,
        "port": SERVICE_PORT,
        "version": "1.0.0",
        "description": "Font Tools Quadratic to Cubic Conversion Service",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "convert": "/convert",
            "info": "/info"
        },
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "max_file_size": "50MB"
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": SERVICE_NAME,
        "status": "running",
        "port": SERVICE_PORT,
        "message": "qu2cu Font Conversion Service is running",
        "endpoints": {
            "health": "/health",
            "ready": "/ready", 
            "convert": "/convert",
            "info": "/info"
        }
    })

if __name__ == '__main__':
    logger.info(f"Starting {SERVICE_NAME} service on port {SERVICE_PORT}")
    try:
        app.run(
            host='0.0.0.0',
            port=SERVICE_PORT,
            debug=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start {SERVICE_NAME} service: {e}")
        sys.exit(1)
