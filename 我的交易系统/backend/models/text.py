"""
Watchlist 模型测试程序
测试自选股列表模型的各项功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.watchlist import Watchlist


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_create_watchlist():
    """测试创建自选列表"""
    print_section("测试1: 创建自选列表")
    
    try:
        # 测试1.1: 创建空列表
        empty_list = Watchlist(
            name="我的关注",
            description="日常关注的股票"
        )
        
        print("✅ 成功创建空列表")
        print(f"   名称: {empty_list.name}")
        print(f"   描述: {empty_list.description}")
        print(f"   股票数量: {empty_list.get_stock_count()}")
        print(f"   是否默认: {bool(empty_list.is_default)}")
        
        # 测试1.2: 创建带股票的列表
        stock_list = Watchlist(
            name="科技股",
            description="科技板块股票",
            stock_codes=["600000.SH", "000001.SZ", "600519.SH"],
            is_default=True
        )
        
        print("\n✅ 成功创建带股票的列表")
        print(f"   名称: {stock_list.name}")
        print(f"   股票数量: {stock_list.get_stock_count()}")
        print(f"   是否默认: {bool(stock_list.is_default)}")
        print(f"   股票列表: {stock_list.get_stocks()}")
        
        # 测试1.3: 从JSON字符串创建
        json_list = Watchlist(
            name="测试列表",
            stock_codes='["600036.SH", "000858.SZ"]'
        )
        
        print("\n✅ 成功从JSON字符串创建列表")
        print(f"   股票列表: {json_list.get_stocks()}")
        
        return empty_list, stock_list
        
    except Exception as e:
        print(f"❌ 创建列表失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_validation_errors():
    """测试验证错误"""
    print_section("测试2: 验证错误处理")
    
    # 测试2.1: 空名称
    try:
        Watchlist(name="")
        print("❌ 应该抛出异常：空名称")
    except ValueError as e:
        print(f"✅ 正确捕获空名称错误: {e}")
    
    # 测试2.2: 名称过长
    try:
        Watchlist(name="A" * 51)
        print("❌ 应该抛出异常：名称过长")
    except ValueError as e:
        print(f"✅ 正确捕获名称过长错误: {e}")
    
    # 测试2.3: 非法字符
    try:
        Watchlist(name="列表@#$%")
        print("❌ 应该抛出异常：非法字符")
    except ValueError as e:
        print(f"✅ 正确捕获非法字符错误: {e}")
    
    # 测试2.4: 无效的股票代码格式
    try:
        Watchlist(
            name="测试",
            stock_codes=["INVALID"]
        )
        print("❌ 应该抛出异常：无效股票代码")
    except ValueError as e:
        print(f"✅ 正确捕获无效股票代码错误")
        print(f"   错误信息包含格式说明: {'支持的格式' in str(e)}")
    
    # 测试2.5: stock_codes类型错误
    try:
        Watchlist(
            name="测试",
            stock_codes=12345  # 应该是列表或字符串
        )
        print("❌ 应该抛出异常：类型错误")
    except TypeError as e:
        print(f"✅ 正确捕获类型错误: {e}")
    
    # 测试2.6: 无效的JSON字符串
    try:
        Watchlist(
            name="测试",
            stock_codes="not a json"
        )
        print("❌ 应该抛出异常：JSON格式错误")
    except ValueError as e:
        print(f"✅ 正确捕获JSON格式错误: {e}")


def test_stock_code_validation():
    """测试股票代码验证"""
    print_section("测试3: 股票代码格式验证")
    
    watchlist = Watchlist(name="测试")
    
    # 测试3.1: 有效的A股代码
    valid_a_stocks = ["600000.SH", "000001.SZ", "834567.BJ"]
    for code in valid_a_stocks:
        result = watchlist._validate_stock_code(code)
        print(f"✅ A股代码 {code} 验证通过 -> {result}")
    
    # 测试3.2: 有效的港股代码
    valid_hk_stocks = ["00700.HK", "09988.HK"]
    for code in valid_hk_stocks:
        result = watchlist._validate_stock_code(code)
        print(f"✅ 港股代码 {code} 验证通过 -> {result}")
    
    # 测试3.3: 有效的美股代码
    valid_us_stocks = ["AAPL.US", "TSLA.NASDAQ", "BABA.NYSE"]
    for code in valid_us_stocks:
        result = watchlist._validate_stock_code(code)
        print(f"✅ 美股代码 {code} 验证通过 -> {result}")
    
    # 测试3.4: 自动转大写
    lowercase_code = watchlist._validate_stock_code("600000.sh")
    print(f"\n✅ 小写代码自动转大写: 600000.sh -> {lowercase_code}")
    
    # 测试3.5: 无效代码
    invalid_codes = ["600000", "SH600000", "ABC", "12345.SH"]
    for code in invalid_codes:
        try:
            watchlist._validate_stock_code(code)
            print(f"❌ 应该拒绝无效代码: {code}")
        except ValueError:
            print(f"✅ 正确拒绝无效代码: {code}")


def test_add_stock():
    """测试添加股票"""
    print_section("测试4: 添加股票")
    
    watchlist = Watchlist(name="测试列表")
    
    # 测试4.1: 添加单只股票
    print("测试4.1: 添加单只股票")
    result = watchlist.add_stock("600000.SH")
    print(f"   添加结果: {result}")
    print(f"   当前股票: {watchlist.get_stocks()}")
    assert result == True
    assert watchlist.get_stock_count() == 1
    print("   ✅ 添加成功")
    
    # 测试4.2: 添加重复股票
    print("\n测试4.2: 添加重复股票")
    try:
        watchlist.add_stock("600000.SH")
        print("   ❌ 应该抛出异常：重复添加")
    except ValueError as e:
        print(f"   ✅ 正确检测到重复: {e}")
    
    # 测试4.3: 添加多只股票
    print("\n测试4.3: 继续添加股票")
    watchlist.add_stock("000001.SZ")
    watchlist.add_stock("600519.SH")
    print(f"   当前股票: {watchlist.get_stocks()}")
    print(f"   股票数量: {watchlist.get_stock_count()}")
    assert watchlist.get_stock_count() == 3
    print("   ✅ 添加成功")


def test_batch_add():
    """测试批量添加"""
    print_section("测试5: 批量添加股票")
    
    watchlist = Watchlist(name="批量测试")
    
    # 测试5.1: 批量添加（包含有效和无效代码）
    print("测试5.1: 混合批量添加")
    result = watchlist.add_stocks_batch([
        "600000.SH",
        "000001.SZ",
        "INVALID_CODE",  # 无效
        "600519.SH",
        "600000.SH",  # 重复（但在本次批量中不算重复）
    ])
    
    print(f"   处理总数: {result['total_processed']}")
    print(f"   成功添加: {result['added']}")
    print(f"   跳过数量: {result['skipped']}")
    print(f"   错误数量: {len(result['errors'])}")
    print(f"   错误详情: {result['errors']}")
    print(f"   当前股票: {watchlist.get_stocks()}")
    
    assert result['added'] == 3  # 600000, 000001, 600519
    assert result['total_processed'] == 5
    assert len(result['errors']) == 1  # INVALID_CODE
    print("   ✅ 批量添加结果正确")
    
    # 测试5.2: 批量添加已存在的股票
    print("\n测试5.2: 批量添加已存在的股票")
    result2 = watchlist.add_stocks_batch([
        "600000.SH",  # 已存在
        "000001.SZ",  # 已存在
        "600036.SH",  # 新股票
    ])
    
    print(f"   成功添加: {result2['added']}")
    print(f"   跳过数量: {result2['skipped']}")
    print(f"   当前股票: {watchlist.get_stocks()}")
    
    assert result2['added'] == 1  # 只有600036
    assert result2['skipped'] == 2  # 600000和000001已存在
    print("   ✅ 去重逻辑正确")


def test_remove_stock():
    """测试移除股票"""
    print_section("测试6: 移除股票")
    
    watchlist = Watchlist(
        name="测试",
        stock_codes=["600000.SH", "000001.SZ", "600519.SH"]
    )
    
    print(f"初始股票: {watchlist.get_stocks()}")
    
    # 测试6.1: 移除存在的股票
    print("\n测试6.1: 移除存在的股票")
    result = watchlist.remove_stock("000001.SZ")
    print(f"   移除结果: {result}")
    print(f"   剩余股票: {watchlist.get_stocks()}")
    assert result == True
    assert watchlist.get_stock_count() == 2
    assert "000001.SZ" not in watchlist.get_stocks()
    print("   ✅ 移除成功")
    
    # 测试6.2: 移除不存在的股票
    print("\n测试6.2: 移除不存在的股票")
    try:
        watchlist.remove_stock("999999.SH")
        print("   ❌ 应该抛出异常：股票不存在")
    except ValueError as e:
        print(f"   ✅ 正确检测到股票不存在: {e}")
    
    # 测试6.3: 大小写不敏感
    print("\n测试6.3: 大小写不敏感移除")
    result = watchlist.remove_stock("600519.sh")  # 小写
    print(f"   移除结果: {result}")
    print(f"   剩余股票: {watchlist.get_stocks()}")
    assert result == True
    print("   ✅ 大小写处理正确")


def test_has_stock():
    """测试检查股票是否存在"""
    print_section("测试7: has_stock() 检查")
    
    watchlist = Watchlist(
        name="测试",
        stock_codes=["600000.SH", "000001.SZ"]
    )
    
    # 测试存在的股票
    assert watchlist.has_stock("600000.SH") == True
    print("✅ 存在的股票返回 True")
    
    # 测试不存在的股票
    assert watchlist.has_stock("999999.SH") == False
    print("✅ 不存在的股票返回 False")
    
    # 测试大小写不敏感
    assert watchlist.has_stock("600000.sh") == True
    print("✅ 大小写不敏感检查正确")


def test_clear_all():
    """测试清空列表"""
    print_section("测试8: clear_all() 清空")
    
    watchlist = Watchlist(
        name="测试",
        stock_codes=["600000.SH", "000001.SZ", "600519.SH"]
    )
    
    print(f"清空前股票数量: {watchlist.get_stock_count()}")
    
    count = watchlist.clear_all()
    
    print(f"清空数量: {count}")
    print(f"清空后股票数量: {watchlist.get_stock_count()}")
    print(f"清空后股票列表: {watchlist.get_stocks()}")
    
    assert count == 3
    assert watchlist.get_stock_count() == 0
    assert watchlist.get_stocks() == []
    print("✅ 清空功能正常")


def test_to_dict():
    """测试序列化"""
    print_section("测试9: to_dict() 序列化")
    
    watchlist = Watchlist(
        name="科技股",
        description="科技板块",
        stock_codes=["600000.SH", "000001.SZ"],
        is_default=True
    )
    
    # 手动设置ID（模拟从数据库查询）
    watchlist.id = 1
    
    # 测试9.1: 完整格式
    print("测试9.1: 完整格式（包含股票列表）")
    result_full = watchlist.to_dict(include_stocks=True)
    print(f"   {result_full}")
    
    assert 'id' in result_full
    assert 'name' in result_full
    assert 'stock_codes' in result_full
    assert 'stock_count' in result_full
    assert result_full['stock_count'] == 2
    assert len(result_full['stock_codes']) == 2
    print("   ✅ 完整格式正确")
    
    # 测试9.2: 简化格式
    print("\n测试9.2: 简化格式（不包含股票列表）")
    result_simple = watchlist.to_dict(include_stocks=False)
    print(f"   {result_simple}")
    
    assert 'stock_codes' not in result_simple
    assert result_simple['stock_count'] == 2
    print("   ✅ 简化格式正确")


def test_string_representation():
    """测试字符串表示"""
    print_section("测试10: __repr__() / __str__()")
    
    watchlist = Watchlist(
        name="我的关注",
        stock_codes=["600000.SH", "000001.SZ", "600519.SH", "600036.SH", "000858.SZ", "600276.SH"]
    )
    watchlist.id = 1
    
    print(f"repr: {repr(watchlist)}")
    print(f"str:  {str(watchlist)}")
    
    # 验证格式
    assert "Watchlist" in repr(watchlist)
    assert "我的关注" in str(watchlist)
    assert "6只股票" in str(watchlist)
    print("\n✅ 字符串表示功能正常")


def test_edge_cases():
    """测试边界情况"""
    print_section("测试11: 边界情况")
    
    # 测试11.1: 空列表操作
    print("测试11.1: 空列表操作")
    empty_list = Watchlist(name="空列表")
    assert empty_list.get_stock_count() == 0
    assert empty_list.get_stocks() == []
    assert empty_list.has_stock("600000.SH") == False
    print("   ✅ 空列表操作正常")
    
    # 测试11.2: 大量股票
    print("\n测试11.2: 大量股票（100只）")
    large_list = Watchlist(name="大量测试")
    stocks = [f"{600000 + i:06d}.SH" for i in range(100)]
    result = large_list.add_stocks_batch(stocks)
    print(f"   添加结果: {result['added']} 只")
    assert result['added'] == 100
    assert large_list.get_stock_count() == 100
    print("   ✅ 大量数据处理正常")
    
    # 测试11.3: 特殊字符名称
    print("\n测试11.3: 特殊字符名称")
    special_list = Watchlist(name="我的 股票_列表123")
    print(f"   列表名称: {special_list.name}")
    assert special_list.name == "我的 股票_列表123"
    print("   ✅ 特殊字符名称处理正常")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print("开始运行 Watchlist 模型测试")
    print("🚀" * 30)
    
    try:
        # 运行所有测试
        test_create_watchlist()
        test_validation_errors()
        test_stock_code_validation()
        test_add_stock()
        test_batch_add()
        test_remove_stock()
        test_has_stock()
        test_clear_all()
        test_to_dict()
        test_string_representation()
        test_edge_cases()
        
        print("\n" + "✅" * 30)
        print("所有测试通过！🎉")
        print("✅" * 30)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)