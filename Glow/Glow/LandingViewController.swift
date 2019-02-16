//
//  LandingViewController.swift
//  Glow
//
//  Created by Kevin J Nguyen on 2/16/19.
//  Copyright © 2019 Kevin J Nguyen. All rights reserved.
//

import UIKit
import SwiftVideoBackground

class LandingViewController: UIViewController {

    @IBOutlet weak var drawButton: UIButton!
    @IBOutlet weak var GlowLabel: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        try? VideoBackground.shared.play(view: view, videoName: "Candolim-Beach", videoType: "mp4")
        
        GlowLabel.layer.shadowColor = UIColor.black.cgColor
        GlowLabel.layer.shadowOffset = CGSize(width: 0.0, height: 2.0)
        GlowLabel.layer.masksToBounds = false
        GlowLabel.layer.shadowRadius = 1.0
        GlowLabel.layer.shadowOpacity = 0.5
        GlowLabel.layer.cornerRadius = drawButton.frame.width / 2
        
        drawButton.layer.shadowColor = UIColor.black.cgColor
        drawButton.layer.shadowOffset = CGSize(width: 0.0, height: 2.0)
        drawButton.layer.masksToBounds = false
        drawButton.layer.shadowRadius = 1.0
        drawButton.layer.shadowOpacity = 0.5
        drawButton.layer.cornerRadius = drawButton.frame.width / 2
        // Do any additional setup after loading the view.
    }
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
