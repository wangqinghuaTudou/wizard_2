import wapi
for a in range(0,500):
	asset_path=wapi.assets.create_asset("assets/props", f"benchmark_{str(a)}")
	for stage in ['modeling', 'rigging', 'texturing', 'grooming', 'shading']:
		wapi.assets.create_stage(asset_path, stage)

# 500 assets & 2500 stages
# 16h47 > 17h03 ( 16min ) 