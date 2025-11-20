#!/usr/bin/env python
"""
简化版Shorts检测测试 - 不需要数据库
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import parse_iso8601_duration

def test_duration_parsing():
    """测试时长解析"""
    print("=" * 60)
    print("YouTube Shorts 检测功能测试（无需数据库）")
    print("=" * 60)
    print()
    
    test_cases = [
        ('PT15S', 15, True),    # 15秒，是Short
        ('PT30S', 30, True),    # 30秒，是Short
        ('PT45S', 45, True),    # 45秒，是Short
        ('PT59S', 59, True),    # 59秒，是Short
        ('PT1M', 60, True),     # 60秒，是Short
        ('PT1M1S', 61, False),  # 61秒，不是Short
        ('PT1M30S', 90, False), # 90秒，不是Short
        ('PT2M', 120, False),   # 2分钟，不是Short
        ('PT2M30S', 150, False), # 2分30秒，不是Short
        ('PT5M', 300, False),   # 5分钟，不是Short
        ('PT10M', 600, False),  # 10分钟，不是Short
        ('PT1H', 3600, False),  # 1小时，不是Short
    ]
    
    print("测试YouTube视频时长解析：")
    print("-" * 60)
    print(f"{'时长格式':<12} {'解析结果':<10} {'是否Shorts':<12} {'测试结果':<10}")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    for duration_str, expected_seconds, expected_is_short in test_cases:
        seconds = parse_iso8601_duration(duration_str)
        is_short = seconds > 0 and seconds <= 60
        
        # 验证结果
        test_passed = (seconds == expected_seconds and is_short == expected_is_short)
        status = "✅ 通过" if test_passed else "❌ 失败"
        
        if test_passed:
            passed += 1
        else:
            failed += 1
        
        short_label = "是" if is_short else "否"
        print(f"{duration_str:<12} {seconds:>6} 秒    {short_label:<12} {status:<10}")
    
    print("-" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print()
    
    return passed, failed

def test_shorts_detection_logic():
    """测试Shorts检测逻辑"""
    print("测试Shorts检测逻辑：")
    print("-" * 60)
    
    test_videos = [
        {
            'title': 'Quick tip in 30 seconds',
            'description': 'A quick tutorial',
            'duration': 'PT30S',
            'expected': True,
            'reason': '时长30秒'
        },
        {
            'title': 'Amazing #Shorts video',
            'description': 'Check this out',
            'duration': 'PT2M',
            'expected': True,
            'reason': '标题含#Shorts'
        },
        {
            'title': 'Regular video',
            'description': 'This is a #shorts video',
            'duration': 'PT5M',
            'expected': True,
            'reason': '描述含#shorts'
        },
        {
            'title': 'Long tutorial',
            'description': 'Complete guide',
            'duration': 'PT10M',
            'expected': False,
            'reason': '超过60秒且无#shorts'
        },
        {
            'title': 'Perfect 60 second video',
            'description': 'Exactly one minute',
            'duration': 'PT1M',
            'expected': True,
            'reason': '刚好60秒'
        },
        {
            'title': 'Just over limit',
            'description': '61 seconds',
            'duration': 'PT1M1S',
            'expected': False,
            'reason': '61秒，超过限制'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, video in enumerate(test_videos, 1):
        duration_seconds = parse_iso8601_duration(video['duration'])
        
        # Shorts判断逻辑
        is_short = False
        detection_reason = ""
        
        if duration_seconds > 0 and duration_seconds <= 60:
            is_short = True
            detection_reason = f"时长{duration_seconds}秒 (≤60秒)"
        elif '#shorts' in video['title'].lower():
            is_short = True
            detection_reason = "标题包含#shorts"
        elif '#shorts' in video['description'].lower():
            is_short = True
            detection_reason = "描述包含#shorts"
        else:
            detection_reason = f"时长{duration_seconds}秒 (>60秒) 且无#shorts标签"
        
        # 验证结果
        test_passed = (is_short == video['expected'])
        status = "✅" if test_passed else "❌"
        
        if test_passed:
            passed += 1
        else:
            failed += 1
        
        print(f"\n测试 {i}: {status}")
        print(f"  标题: {video['title']}")
        print(f"  时长: {video['duration']} ({duration_seconds}秒)")
        print(f"  检测结果: {'Shorts' if is_short else '普通视频'}")
        print(f"  检测原因: {detection_reason}")
        print(f"  预期结果: {'Shorts' if video['expected'] else '普通视频'}")
        print(f"  预期原因: {video['reason']}")
    
    print()
    print("-" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print()
    
    return passed, failed

def test_edge_cases():
    """测试边界情况"""
    print("测试边界情况：")
    print("-" * 60)
    
    edge_cases = [
        {
            'name': '空时长',
            'duration': '',
            'expected_seconds': 0,
            'expected_is_short': False
        },
        {
            'name': '只有秒',
            'duration': 'PT59S',
            'expected_seconds': 59,
            'expected_is_short': True
        },
        {
            'name': '只有分钟',
            'duration': 'PT1M',
            'expected_seconds': 60,
            'expected_is_short': True
        },
        {
            'name': '复杂格式',
            'duration': 'PT1H2M3S',
            'expected_seconds': 3723,
            'expected_is_short': False
        },
        {
            'name': '无效格式',
            'duration': 'INVALID',
            'expected_seconds': 0,
            'expected_is_short': False
        }
    ]
    
    passed = 0
    failed = 0
    
    for case in edge_cases:
        try:
            seconds = parse_iso8601_duration(case['duration'])
            is_short = seconds > 0 and seconds <= 60
            
            test_passed = (seconds == case['expected_seconds'] and 
                          is_short == case['expected_is_short'])
            
            if test_passed:
                print(f"✅ {case['name']:<15} - 时长: {case['duration']:<10} -> {seconds}秒")
                passed += 1
            else:
                print(f"❌ {case['name']:<15} - 时长: {case['duration']:<10} -> {seconds}秒 (预期: {case['expected_seconds']}秒)")
                failed += 1
                
        except Exception as e:
            print(f"❌ {case['name']:<15} - 错误: {e}")
            failed += 1
    
    print()
    print("-" * 60)
    print(f"边界测试结果: {passed} 通过, {failed} 失败")
    print()
    
    return passed, failed

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("YouTube Shorts 检测功能测试（简化版）")
    print("=" * 60)
    print()
    
    total_passed = 0
    total_failed = 0
    
    # 运行测试
    p1, f1 = test_duration_parsing()
    total_passed += p1
    total_failed += f1
    
    p2, f2 = test_shorts_detection_logic()
    total_passed += p2
    total_failed += f2
    
    p3, f3 = test_edge_cases()
    total_passed += p3
    total_failed += f3
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {total_passed + total_failed}")
    print(f"✅ 通过: {total_passed}")
    print(f"❌ 失败: {total_failed}")
    
    if total_failed == 0:
        print("\n🎉 所有测试通过！Shorts检测功能工作正常。")
    else:
        print(f"\n⚠️ 有 {total_failed} 个测试失败，请检查代码。")
    
    print()
    print("提示：")
    print("1. 如需测试数据库功能，请先运行: python migrate_database.py")
    print("2. 如需更新现有数据，运行: python update_shorts_field.py")
    print("3. 如需分析Shorts数据，运行: python shorts_analyzer.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\n按Enter键退出...")
