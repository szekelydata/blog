angular.module('app', []);

angular.module('app').controller('mainCntrl', ['$scope', 
function ($scope) {

  $scope.master = {}; // MASTER DATA STORED BY YEAR

  $scope.selected_year = 2014;
  $scope.years = d3.range(2014, 1950, -1);

  $scope.filters = {};
  $scope.hasFilters = false;
  var steps=[0.005,0.01,0.05,0.1,0.5,1,5,10]
  $scope.th=1;
  $scope.idp=false;
  var steps2=[0.01,0.05,0.1,0.5,1,5,10,1000]
  $scope.th2=6;
  //$scope.filters = {"Germany":{"hide":true,"name":"Germany"},"DRC":{"hide":true,"name":"DRC"},};
  //$scope.hasFilters = true;
  
  var europe=[	"Afganisztán"
				];
					
  
  new Dragdealer("sizefilter", {
		x: 1/7,
		steps: 8,
		snap: true,
		animationCallback: function(a, b) {
			d3.select("#sizefilterhandle").text(steps[Math.round(7 * a)]+'e');
		},
		callback: function(a, b) {
			$scope.th = Math.round(7 * a);
			$scope.update();
		}
	});
  new Dragdealer("sizefilter2", {
		x: 6/7,
		steps: 8,
		snap: true,
		animationCallback: function(a, b) {
			d3.select("#sizefilterhandle2").text(steps2[Math.round(7 * a)]+'e');
		},
		callback: function(a, b) {
			$scope.th2 = Math.round(7 * a);
			$scope.update();
		}
	});
	
	
  $scope.tooltip = {};

  // FORMATS USED IN TOOLTIP TEMPLATE IN HTML
  $scope.pFormat = d3.format(".1%");  // PERCENT FORMAT
  $scope.qFormat = d3.format(",.0f"); // COMMAS FOR LARGE NUMBERS

  $scope.updateTooltip = function (data) {
    $scope.tooltip = data;
    $scope.$apply();
  }

  $scope.addFilter = function (name) {
    $scope.hasFilters = true;
    $scope.filters[name] = {
      name: name,
      hide: true
    };
    $scope.$apply();
  };
  
  $scope.update = function () {
	d3.select("#idp").text(function(){if ($scope.idp) return "IDPk ki"; else return "IDPk be"});
    var data2 = $scope.master[$scope.selected_year];	
	if (data2) {
		var data=data2.filter(function (d) {
			if ( ((d.flow1>steps[$scope.th]*1000) || (d.flow2>steps[$scope.th]*1000)) && ((d.flow1<steps2[$scope.th2]*1000) && (d.flow2<steps2[$scope.th2]*1000)) ) {
				if (!((d.importer1==d.importer2) && ($scope.idp))) {
					if (($.inArray(d.importer2, europe)!=-1)||($.inArray(d.importer1, europe)!=-1)) {
						return true;
					}
				}
			}
			return false;
		})
	}  
    if (data && $scope.hasFilters) {
        $scope.drawChords(data.filter(function (d) {
        var fl = $scope.filters;
        var v1 = d.importer1, v2 = d.importer2;

        if ((fl[v1] && fl[v1].hide) || (fl[v2] && fl[v2].hide)) {
          return false;
        }
        return true;
      }));
    } else if (data) {
      $scope.drawChords(data);
    
		var totalUnitPrice = 0;
		for (i in data){
			totalUnitPrice+=data[i].flow1+data[i].flow2;
		}
		d3.select("#total").transition().duration(1000).style("opacity","0");
		d3.select("#total").transition().delay(1000).text(Math.round(totalUnitPrice/1000)+"E");
		d3.select("#total").transition().delay(1000).duration(1000).style("opacity","1");
	}
  };

  // IMPORT THE CSV DATA
  d3.csv('datab.csv', function (err, data) {

    data.forEach(function (d) {
      d.year  = +d.year;
      d.flow1 = +d.flow1;
      d.flow2 = +d.flow2;

      if (!$scope.master[d.year]) {
        $scope.master[d.year] = []; // STORED BY YEAR
      }
      $scope.master[d.year].push(d);
    })
    $scope.update();
  });

  $scope.$watch('selected_year', $scope.update);
  $scope.$watch('filters', $scope.update, true);
  $scope.$watch('idp', $scope.update);

}]);