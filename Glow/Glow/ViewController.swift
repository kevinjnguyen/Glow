//
//  ViewController.swift
//  Glow
//
//  Created by Kevin J Nguyen on 2/15/19.
//  Copyright © 2019 Kevin J Nguyen. All rights reserved.
//

import UIKit
import SwiftGRPC
import SwiftVideoBackground

class ViewController: UIViewController {

    @IBOutlet weak var mainImageView: UIImageView!
    @IBOutlet weak var tempImageView: UIImageView!
    
    var lastPoint = CGPoint.zero
    var color = UIColor.black
    var brushWidth: CGFloat = 10.0
    var opacity: CGFloat = 1.0
    var swiped = false
    
    let glow_rep = GlowRepository.shared
    
    var points: [(CGPoint, CGPoint)] = []
    
    var isSending: Bool = false
    var info = Glow_GlowReply()
    
    override func viewDidLoad() {
        super.viewDidLoad()
    }

    @IBAction func resetTouchBegan(_ sender: Any) {
        mainImageView.image = nil
        self.isSending = false;
        self.points = []
    }
    
    @IBAction func didPressBack(_ sender: Any) {
        self.dismiss(animated: true, completion: nil)
    }
    func drawLine(from fromPoint: CGPoint, to toPoint: CGPoint) {
        
        if (isSending) {
            return
        }
        
        if (fromPoint.y < 256.0) {
            return;
        }
        
        points.append((fromPoint, toPoint))
        
        var sendPoint = Glow_PointRequest()
        sendPoint.x1 = Int32(Int(fromPoint.x * 10))
        sendPoint.x2 =  Int32(Int(toPoint.x * 10))
        sendPoint.y1 =  Int32(Int(fromPoint.y * 10))
        sendPoint.y2 =  Int32(Int(toPoint.y * 10))
        do {
            try glow_rep.sendPoint(point: sendPoint)
        } catch {
            print("error")
        }
        
        UIGraphicsBeginImageContext(view.frame.size)
        guard let context = UIGraphicsGetCurrentContext() else {
            return
        }
        tempImageView.image?.draw(in: view.bounds)
        
        context.move(to: fromPoint)
        context.addLine(to: toPoint)
        
        context.setLineCap(.round)
        context.setBlendMode(.normal)
        context.setLineWidth(brushWidth)
        context.setStrokeColor(color.cgColor)
        
        context.strokePath()
        
        tempImageView.image = UIGraphicsGetImageFromCurrentImageContext()
        tempImageView.alpha = opacity
        
        UIGraphicsEndImageContext()
    }
    
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else {
            return
        }
        swiped = false
        lastPoint = touch.location(in: view)
    }
    
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else {
            return
        }
        swiped = true
        let currentPoint = touch.location(in: view)
        drawLine(from: lastPoint, to: currentPoint)
        
        lastPoint = currentPoint
    }
    
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        if !swiped {
            // draw a single point
            drawLine(from: lastPoint, to: lastPoint)
        }
        
        // Merge tempImageView into mainImageView
        UIGraphicsBeginImageContext(mainImageView.frame.size)
        mainImageView.image?.draw(in: view.bounds, blendMode: .normal, alpha: 1.0)
        tempImageView?.image?.draw(in: view.bounds, blendMode: .normal, alpha: opacity)
        mainImageView.image = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext()
        
        tempImageView.image = nil
    }

}

