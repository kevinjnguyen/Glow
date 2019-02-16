//
//  GlowRepository.swift
//  Glow
//
//  Created by Kevin J Nguyen on 2/16/19.
//  Copyright © 2019 Kevin J Nguyen. All rights reserved.
//

import Foundation
import SwiftGRPC

class GlowRepository {
    
    static let RASPBERRY_IP = "192.168.43.144:50051"
    static let shared = GlowRepository()
    private init() {}
    private let client = Glow_GlowServiceClient.init(address: RASPBERRY_IP, secure: false)
    
    func sendPoint(point: Glow_PointRequest) throws {
        try client.testPointReceiving(point)
    }
}
